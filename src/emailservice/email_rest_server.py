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
import os
import ssl
import json
import urllib3
import random
import uvicorn
from fastapi import FastAPI
from typing import List, Optional, Type
from fastapi import FastAPI, Query, Depends
from pydantic import BaseModel
restPort=os.environ.get('REST_PORT')

app=FastAPI()

@app.post("/send-order-confirmation")
async def sendConfirmation():
    print("Sending Email confirmation")
    return {"status":"200 OK"}

def startRest(port):
     uvicorn.run(
         "email_rest_server:app",
         host="0.0.0.0",
         port=int(port))

