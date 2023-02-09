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

from thrift.Thrift import TProcessor, TMessageType
from thrift.protocol import TProtocolDecorator, TMultiplexedProtocol
from thrift.protocol.TProtocol import TProtocolException


class TMultiplexedProcessor(TProcessor):
    def __init__(self):
        self.defaultProcessor = None
        self.services = {}

    def registerDefault(self, processor):
        """
        If a non-multiplexed processor connects to the server and wants to
        communicate, use the given processor to handle it.  This mechanism
        allows servers to upgrade from non-multiplexed to multiplexed in a
        backwards-compatible way and still handle old clients.
        """
        self.defaultProcessor = processor

    def registerProcessor(self, serviceName, processor):
        self.services[serviceName] = processor

    def on_message_begin(self, func):
        for key in self.services.keys():
            self.services[key].on_message_begin(func)

    def process(self, iprot, oprot):
        (name, type, seqid) = iprot.readMessageBegin()
        if type != TMessageType.CALL and type != TMessageType.ONEWAY:
            raise TProtocolException(
                TProtocolException.NOT_IMPLEMENTED,
                "TMultiplexedProtocol only supports CALL & ONEWAY")

        index = name.find(TMultiplexedProtocol.SEPARATOR)
        if index < 0:
            if self.defaultProcessor:
                return self.defaultProcessor.process(
                    StoredMessageProtocol(iprot, (name, type, seqid)), oprot)
            else:
                raise TProtocolException(
                    TProtocolException.NOT_IMPLEMENTED,
                    "Service name not found in message name: " + name + ".  " +
                    "Did you forget to use TMultiplexedProtocol in your client?")

        serviceName = name[0:index]
        call = name[index + len(TMultiplexedProtocol.SEPARATOR):]
        if serviceName not in self.services:
            raise TProtocolException(
                TProtocolException.NOT_IMPLEMENTED,
                "Service name not found: " + serviceName + ".  " +
                "Did you forget to call registerProcessor()?")

        standardMessage = (call, type, seqid)
        return self.services[serviceName].process(
            StoredMessageProtocol(iprot, standardMessage), oprot)


class StoredMessageProtocol(TProtocolDecorator.TProtocolDecorator):
    def __init__(self, protocol, messageBegin):
        self.messageBegin = messageBegin

    def readMessageBegin(self):
        return self.messageBegin
