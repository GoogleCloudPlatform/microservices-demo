#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import errno
import logging
import os
import socket
import sys

from .TTransport import TTransportBase, TTransportException, TServerTransportBase

logger = logging.getLogger(__name__)


class TSocketBase(TTransportBase):
    def _resolveAddr(self):
        if self._unix_socket is not None:
            return [(socket.AF_UNIX, socket.SOCK_STREAM, None, None,
                     self._unix_socket)]
        else:
            return socket.getaddrinfo(self.host,
                                      self.port,
                                      self._socket_family,
                                      socket.SOCK_STREAM,
                                      0,
                                      socket.AI_PASSIVE)

    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None


class TSocket(TSocketBase):
    """Socket implementation of TTransport base."""

    def __init__(self, host='localhost', port=9090, unix_socket=None,
                 socket_family=socket.AF_UNSPEC,
                 socket_keepalive=False):
        """Initialize a TSocket

        @param host(str)  The host to connect to.
        @param port(int)  The (TCP) port to connect to.
        @param unix_socket(str)  The filename of a unix socket to connect to.
                                 (host and port will be ignored.)
        @param socket_family(int)  The socket family to use with this socket.
        @param socket_keepalive(bool) enable TCP keepalive, default off.
        """
        self.host = host
        self.port = port
        self.handle = None
        self._unix_socket = unix_socket
        self._timeout = None
        self._socket_family = socket_family
        self._socket_keepalive = socket_keepalive

    def setHandle(self, h):
        self.handle = h

    def isOpen(self):
        if self.handle is None:
            return False

        # this lets us cheaply see if the other end of the socket is still
        # connected. if disconnected, we'll get EOF back (expressed as zero
        # bytes of data) otherwise we'll get one byte or an error indicating
        # we'd have to block for data.
        #
        # note that we're not doing this with socket.MSG_DONTWAIT because 1)
        # it's linux-specific and 2) gevent-patched sockets hide EAGAIN from us
        # when timeout is non-zero.
        original_timeout = self.handle.gettimeout()
        try:
            self.handle.settimeout(0)
            try:
                peeked_bytes = self.handle.recv(1, socket.MSG_PEEK)
            except (socket.error, OSError) as exc:  # on modern python this is just BlockingIOError
                if exc.errno in (errno.EWOULDBLOCK, errno.EAGAIN):
                    return True
                return False
        finally:
            self.handle.settimeout(original_timeout)

        # the length will be zero if we got EOF (indicating connection closed)
        return len(peeked_bytes) == 1

    def setTimeout(self, ms):
        if ms is None:
            self._timeout = None
        else:
            self._timeout = ms / 1000.0

        if self.handle is not None:
            self.handle.settimeout(self._timeout)

    def _do_open(self, family, socktype):
        return socket.socket(family, socktype)

    @property
    def _address(self):
        return self._unix_socket if self._unix_socket else '%s:%d' % (self.host, self.port)

    def open(self):
        if self.handle:
            raise TTransportException(type=TTransportException.ALREADY_OPEN, message="already open")
        try:
            addrs = self._resolveAddr()
        except socket.gaierror as gai:
            msg = 'failed to resolve sockaddr for ' + str(self._address)
            logger.exception(msg)
            raise TTransportException(type=TTransportException.NOT_OPEN, message=msg, inner=gai)
        for family, socktype, _, _, sockaddr in addrs:
            handle = self._do_open(family, socktype)

            # TCP_KEEPALIVE
            if self._socket_keepalive:
                handle.setsockopt(socket.IPPROTO_TCP, socket.SO_KEEPALIVE, 1)

            handle.settimeout(self._timeout)
            try:
                handle.connect(sockaddr)
                self.handle = handle
                return
            except socket.error:
                handle.close()
                logger.info('Could not connect to %s', sockaddr, exc_info=True)
        msg = 'Could not connect to any of %s' % list(map(lambda a: a[4],
                                                          addrs))
        logger.error(msg)
        raise TTransportException(type=TTransportException.NOT_OPEN, message=msg)

    def read(self, sz):
        try:
            buff = self.handle.recv(sz)
        except socket.error as e:
            if (e.args[0] == errno.ECONNRESET and
                    (sys.platform == 'darwin' or sys.platform.startswith('freebsd'))):
                # freebsd and Mach don't follow POSIX semantic of recv
                # and fail with ECONNRESET if peer performed shutdown.
                # See corresponding comment and code in TSocket::read()
                # in lib/cpp/src/transport/TSocket.cpp.
                self.close()
                # Trigger the check to raise the END_OF_FILE exception below.
                buff = ''
            elif e.args[0] == errno.ETIMEDOUT:
                raise TTransportException(type=TTransportException.TIMED_OUT, message="read timeout", inner=e)
            else:
                raise TTransportException(message="unexpected exception", inner=e)
        if len(buff) == 0:
            raise TTransportException(type=TTransportException.END_OF_FILE,
                                      message='TSocket read 0 bytes')
        return buff

    def write(self, buff):
        if not self.handle:
            raise TTransportException(type=TTransportException.NOT_OPEN,
                                      message='Transport not open')
        sent = 0
        have = len(buff)
        while sent < have:
            try:
                plus = self.handle.send(buff)
                if plus == 0:
                    raise TTransportException(type=TTransportException.END_OF_FILE,
                                              message='TSocket sent 0 bytes')
                sent += plus
                buff = buff[plus:]
            except socket.error as e:
                raise TTransportException(message="unexpected exception", inner=e)

    def flush(self):
        pass


class TServerSocket(TSocketBase, TServerTransportBase):
    """Socket implementation of TServerTransport base."""

    def __init__(self, host=None, port=9090, unix_socket=None, socket_family=socket.AF_UNSPEC):
        self.host = host
        self.port = port
        self._unix_socket = unix_socket
        self._socket_family = socket_family
        self.handle = None
        self._backlog = 128

    def setBacklog(self, backlog=None):
        if not self.handle:
            self._backlog = backlog
        else:
            # We cann't update backlog when it is already listening, since the
            # handle has been created.
            logger.warn('You have to set backlog before listen.')

    def listen(self):
        res0 = self._resolveAddr()
        socket_family = self._socket_family == socket.AF_UNSPEC and socket.AF_INET6 or self._socket_family
        for res in res0:
            if res[0] is socket_family or res is res0[-1]:
                break

        # We need remove the old unix socket if the file exists and
        # nobody is listening on it.
        if self._unix_socket:
            tmp = socket.socket(res[0], res[1])
            try:
                tmp.connect(res[4])
            except socket.error as err:
                eno, message = err.args
                if eno == errno.ECONNREFUSED:
                    os.unlink(res[4])

        self.handle = socket.socket(res[0], res[1])
        self.handle.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(self.handle, 'settimeout'):
            self.handle.settimeout(None)
        self.handle.bind(res[4])
        self.handle.listen(self._backlog)

    def accept(self):
        client, addr = self.handle.accept()
        result = TSocket()
        result.setHandle(client)
        return result
