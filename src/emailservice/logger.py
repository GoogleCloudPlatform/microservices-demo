#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys
import json

class JSONStreamHandler(logging.StreamHandler):
  """JSONStreamHandler emits log data in JSON format to stdout"""

  def __init__(self):
    super().__init__(sys.stdout)

  def emit(self, record):
    try:
      msg = super().format(record)
      data = {
        'message': msg,
        'severity': record.levelname,
        'name': 'emailservice'
      }
      stream = self.stream
      stream.write(json.dumps(data)+'\n')
      self.flush()
    except (KeyboardInterrupt, SystemExit):
      raise
    except:
      self.handleError(record)
