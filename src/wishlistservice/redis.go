// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"net"
	"strconv"
	"strings"
	"sync"
	"time"
)

// This service only needs a dozen Redis commands, so instead of pulling in a
// full client library it speaks RESP (the Redis wire protocol) directly over a
// small connection pool. That keeps the module dependency-free, which in turn
// keeps the container build fast and reproducible.

const (
	redisDialTimeout = 3 * time.Second
	redisRWTimeout   = 3 * time.Second
	redisMaxIdle     = 8
)

// errRedisConn signals a transport level failure, which means the pooled
// connection must be discarded instead of reused.
var errRedisConn = errors.New("redis: connection failure")

type redisClient struct {
	addr string

	mu   sync.Mutex
	idle []*redisConn
}

type redisConn struct {
	c  net.Conn
	br *bufio.Reader
}

func newRedisClient(addr string) *redisClient {
	return &redisClient{addr: addr}
}

func (r *redisClient) dial() (*redisConn, error) {
	c, err := net.DialTimeout("tcp", r.addr, redisDialTimeout)
	if err != nil {
		return nil, fmt.Errorf("%w: %v", errRedisConn, err)
	}
	return &redisConn{c: c, br: bufio.NewReader(c)}, nil
}

func (r *redisClient) get() (*redisConn, error) {
	r.mu.Lock()
	if n := len(r.idle); n > 0 {
		conn := r.idle[n-1]
		r.idle = r.idle[:n-1]
		r.mu.Unlock()
		return conn, nil
	}
	r.mu.Unlock()
	return r.dial()
}

func (r *redisClient) put(conn *redisConn) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if len(r.idle) >= redisMaxIdle {
		conn.c.Close()
		return
	}
	r.idle = append(r.idle, conn)
}

// do runs one command. A connection level error is retried once on a fresh
// connection, which covers the common case of Redis recycling idle sockets.
func (r *redisClient) do(args ...string) (*reply, error) {
	res, err := r.doOnce(args...)
	if err != nil && errors.Is(err, errRedisConn) {
		res, err = r.doOnce(args...)
	}
	return res, err
}

func (r *redisClient) doOnce(args ...string) (*reply, error) {
	conn, err := r.get()
	if err != nil {
		return nil, err
	}
	if err := conn.c.SetDeadline(time.Now().Add(redisRWTimeout)); err != nil {
		conn.c.Close()
		return nil, fmt.Errorf("%w: %v", errRedisConn, err)
	}
	if _, err := conn.c.Write(encodeCommand(args)); err != nil {
		conn.c.Close()
		return nil, fmt.Errorf("%w: %v", errRedisConn, err)
	}
	res, err := readReply(conn.br)
	if err != nil {
		if errors.Is(err, errRedisConn) {
			conn.c.Close()
			return nil, err
		}
		// A command error (for example WRONGTYPE) leaves the connection in a
		// perfectly usable state, so it goes back to the pool.
		r.put(conn)
		return nil, err
	}
	r.put(conn)
	return res, nil
}

func encodeCommand(args []string) []byte {
	var b strings.Builder
	b.WriteString("*" + strconv.Itoa(len(args)) + "\r\n")
	for _, a := range args {
		b.WriteString("$" + strconv.Itoa(len(a)) + "\r\n")
		b.WriteString(a)
		b.WriteString("\r\n")
	}
	return []byte(b.String())
}

type reply struct {
	kind  byte
	str   string
	num   int64
	null  bool
	array []*reply
}

func (r *reply) strings() []string {
	if r == nil {
		return nil
	}
	out := make([]string, 0, len(r.array))
	for _, e := range r.array {
		out = append(out, e.str)
	}
	return out
}

func readLine(br *bufio.Reader) (string, error) {
	line, err := br.ReadString('\n')
	if err != nil {
		return "", fmt.Errorf("%w: %v", errRedisConn, err)
	}
	if len(line) < 2 {
		return "", fmt.Errorf("%w: short reply line", errRedisConn)
	}
	return line[:len(line)-2], nil
}

func readReply(br *bufio.Reader) (*reply, error) {
	line, err := readLine(br)
	if err != nil {
		return nil, err
	}
	switch line[0] {
	case '+':
		return &reply{kind: '+', str: line[1:]}, nil
	case '-':
		return nil, errors.New("redis: " + line[1:])
	case ':':
		n, err := strconv.ParseInt(line[1:], 10, 64)
		if err != nil {
			return nil, fmt.Errorf("%w: bad integer reply", errRedisConn)
		}
		return &reply{kind: ':', num: n}, nil
	case '$':
		n, err := strconv.Atoi(line[1:])
		if err != nil {
			return nil, fmt.Errorf("%w: bad bulk length", errRedisConn)
		}
		if n < 0 {
			return &reply{kind: '$', null: true}, nil
		}
		buf := make([]byte, n+2) // payload + CRLF
		if _, err := io.ReadFull(br, buf); err != nil {
			return nil, fmt.Errorf("%w: %v", errRedisConn, err)
		}
		return &reply{kind: '$', str: string(buf[:n])}, nil
	case '*':
		n, err := strconv.Atoi(line[1:])
		if err != nil {
			return nil, fmt.Errorf("%w: bad array length", errRedisConn)
		}
		if n < 0 {
			return &reply{kind: '*', null: true}, nil
		}
		out := &reply{kind: '*', array: make([]*reply, 0, n)}
		for i := 0; i < n; i++ {
			e, err := readReply(br)
			if err != nil {
				return nil, err
			}
			out.array = append(out.array, e)
		}
		return out, nil
	default:
		return nil, fmt.Errorf("%w: unknown reply type %q", errRedisConn, line[0])
	}
}
