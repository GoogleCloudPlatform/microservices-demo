// Copyright 2022 Skyramp, Inc.
//
//	Licensed under the Apache License, Version 2.0 (the "License");
//	you may not use this file except in compliance with the License.
//	You may obtain a copy of the License at
//
//	http://www.apache.org/licenses/LICENSE-2.0
//
//	Unless required by applicable law or agreed to in writing, software
//	distributed under the License is distributed on an "AS IS" BASIS,
//	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//	See the License for the specific language governing permissions and
//	limitations under the License.
package main

import (
	"crypto/tls"
	"fmt"
	"net/http"

	"github.com/apache/thrift/lib/go/thrift"
)

type ThriftProtocolType string

const (
	Binary     ThriftProtocolType = "binary"
	Json       ThriftProtocolType = "json"
	SimpleJson ThriftProtocolType = "simplejson"
	Compact    ThriftProtocolType = "compact"
)

type Option struct {
	HttpTransport bool
	HttpUrl       string
	Protocol      ThriftProtocolType
	Secure        bool
	Buffered      bool
	Framed        bool
}

func NewDefaultOption() *Option {
	return &Option{
		Protocol:      Binary,
		HttpTransport: true,
		Secure:        false,
		Buffered:      true,
		Framed:        false,
	}
}

var (
	protocolFactoryMap          = make(map[ThriftProtocolType]thrift.TProtocolFactory)
	bufferedTransportFactoryMap = make(map[bool]thrift.TTransportFactory)
)

func init() {
	protocolFactoryMap[Binary] = thrift.NewTBinaryProtocolFactoryConf(nil)
	protocolFactoryMap[Json] = thrift.NewTJSONProtocolFactory()
	protocolFactoryMap[SimpleJson] = thrift.NewTSimpleJSONProtocolFactoryConf(nil)
	protocolFactoryMap[Compact] = thrift.NewTCompactProtocolFactoryConf(nil)
	bufferedTransportFactoryMap[true] = thrift.NewTBufferedTransportFactory(8192)
	bufferedTransportFactoryMap[false] = thrift.NewTTransportFactory()
}

/*
 * Creats a ThriftServer with autogenerated certificate
 */
func NewHttpThriftServer(addr string, opt *Option, processor thrift.TProcessor) error {
	printStatus(addr, opt)
	protocolFactory := protocolFactoryMap[opt.Protocol]
	if !opt.HttpTransport {
		return fmt.Errorf("NewHttpThriftServer called with opt.httpTransport set to [false]")
	}

	http.HandleFunc(opt.HttpUrl, thrift.NewThriftHandlerFunc(processor, protocolFactory, protocolFactory))
	log.Infof("tcp listener opened for thrift socket %s", addr)
	var err error
	if opt.Secure {
		err = startHttps(addr)
	} else {
		err = http.ListenAndServe(addr, nil)
	}
	if err != nil {
		log.Errorf("failed to start http server: %v", err)
	}
	return nil
}

/*
 * Creats a ThriftServer with provided key and certificate
 */
func NewHttpThriftServer2(addr string, opt *Option, certFile, keyFile string, processor thrift.TProcessor) error {
	printStatus(addr, opt)
	protocolFactory := protocolFactoryMap[opt.Protocol]
	if !opt.HttpTransport {
		return fmt.Errorf("NewHttpThriftServer called with opt.httpTransport set to [false]")
	}
	http.HandleFunc(opt.HttpUrl, thrift.NewThriftHandlerFunc(processor, protocolFactory, protocolFactory))
	var err error
	if opt.Secure {
		err = http.ListenAndServeTLS(addr, certFile, keyFile, nil)
	} else {
		err = http.ListenAndServe(addr, nil)
	}
	if err != nil {
		fmt.Printf("Failed to start http server: %v\n", err)
	}
	return nil
}

func printStatus(addr string, opt *Option) {
	log.Infof("creating a mocked thrift service on %s with options:", addr)
	log.Infof("protocol: [%s], httpTransport: [%t], secure: [%t], buffered: [%t], framed: [%t]",
		opt.Protocol, opt.HttpTransport, opt.Secure, opt.Buffered, opt.Framed)
}

func NewStandardThriftServer(addr string, opt *Option, processor thrift.TProcessor) error {
	printStatus(addr, opt)
	protocolFactory, ok := protocolFactoryMap[opt.Protocol]
	if !ok {
		return fmt.Errorf("no protocol found for NewThriftServer %s", opt.Protocol)
	}

	var transportFactory thrift.TTransportFactory
	cfg := &thrift.TConfiguration{
		TLSConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	}
	transportFactory = bufferedTransportFactoryMap[opt.Buffered]

	if opt.Framed {
		transportFactory = thrift.NewTFramedTransportFactoryConf(transportFactory, cfg)
	}
	var transport thrift.TServerTransport
	var err error
	if opt.Secure {
		serverTLSConf, clientTLSConf, caPEM, err := generateCertificate()
		_, _ = clientTLSConf, caPEM
		if err != nil {
			return fmt.Errorf("failed to create tls certificate %w", err)
		}
		transport, err = thrift.NewTSSLServerSocket(addr, serverTLSConf)
		if err != nil {
			return fmt.Errorf("failed to create tls certificate %w", err)
		}
	} else {
		transport, err = thrift.NewTServerSocket(addr)
		if err != nil {
			return fmt.Errorf("failed to create thrift server %w", err)
		}
	}
	log.Infof("tcp listener opened for thrift socket %s", addr)
	server := thrift.NewTSimpleServer4(processor, transport, transportFactory, protocolFactory)
	err = server.Serve()
	if err != nil {
		return fmt.Errorf("failed to start Thrift server... on port %s", addr)
	}
	log.Infof("thrift service... on port %s terminated \n", addr)
	return nil
}

// Starts https with in memory generated certificate
func startHttps(addr string) error {
	serverTLSConf, clientTLSConf, caPEM, _ := generateCertificate()
	_, _ = clientTLSConf, caPEM
	getCertificate := func(info *tls.ClientHelloInfo) (*tls.Certificate, error) {
		return &serverTLSConf.Certificates[0], nil
	}

	srv := &http.Server{
		Addr:    addr,
		Handler: http.DefaultServeMux,
		TLSConfig: &tls.Config{
			MinVersion:     tls.VersionTLS13,
			GetCertificate: getCertificate,
		},
	}
	err := srv.ListenAndServeTLS("", "")
	if err != nil {
		fmt.Println("failed to perform https listen and serve tls %w", err)
		return fmt.Errorf("failed to perform https listen and serve tls %w", err)
	}
	return nil
}

/*
*  Return a new ThriftClient
 */
func NewThriftClient(hostPort string, opt *Option) (client *thrift.TStandardClient, trans thrift.TTransport, err error) {

	cfg := &thrift.TConfiguration{
		TLSConfig: &tls.Config{
			InsecureSkipVerify: true,
		},
	}

	protocolFactory := protocolFactoryMap[opt.Protocol]
	if opt.Secure {
		trans = thrift.NewTSSLSocketConf(hostPort, cfg)
	} else {
		trans = thrift.NewTSocketConf(hostPort, nil)
	}
	if err != nil {
		return nil, nil, err
	}
	if opt.HttpTransport {
		if opt.Secure {
			tr := &http.Transport{
				TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
			}
			client := &http.Client{Transport: tr}
			trans, err = thrift.NewTHttpClientWithOptions(fmt.Sprintf("https://%s%s", hostPort, opt.HttpUrl), thrift.THttpClientOptions{Client: client})
		} else {
			trans, err = thrift.NewTHttpClient(fmt.Sprintf("http://%s%s", hostPort, opt.HttpUrl))
		}
	} else {
		if opt.Buffered {
			trans = thrift.NewTBufferedTransport(trans, 8192)
		} else {
			trans = thrift.NewTFramedTransportConf(trans, cfg)
		}
	}
	if err != nil {
		return nil, nil, err
	}
	iprot := protocolFactory.GetProtocol(trans)
	oprot := protocolFactory.GetProtocol(trans)
	client = thrift.NewTStandardClient(iprot, oprot)
	return
}
