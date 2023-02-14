# Copyright 2022 Skyramp, Inc.
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.
from thrift.server import THttpServer
from thrift.protocol import TBinaryProtocol
from thriftpy.demo import EmailService


class DummyEmailThriftService(EmailService.Iface):
    def SendOrderConfirmation(self, email, order):
        print(f"A request to send order confirmation email to {email} for order {order} has been received.")
        return

def main(port, dummy_mode):
    if dummy_mode:
        processor = EmailService.Processor(DummyEmailThriftService())
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = THttpServer.THttpServer(
            processor,
            ('', port),
            pfactory
        )
        print(f'Starting thrift server on port {port}')
        server.serve()
    else:
        raise Exception('non-dummy mode not implemented yet')

def startThrift(port):
  main(port,  dummy_mode = True)
