# Copyright 2020 Google LLC
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

FROM python:3.8-slim as base

FROM base as builder

COPY requirements.txt .

RUN pip install --prefix="/install" -r requirements.txt


FROM base


WORKDIR /loadgen

RUN pip install sealights-python-agent

COPY sltoken.txt sltoken.txt

# Add application code.
COPY locustfile.py .

RUN ls -l

RUN sl-python config  --appname loadgenerator --branchname master --buildname load-1.1.3 --token eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL1BST0QtQ1VTVE9NRVJTMi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IlBST0QtQ1VTVE9NRVJTMixuZWVkVG9SZW1vdmUsQVBJR1ctZDk5MWY3YWMtMDc2MC00OTQ4LWIzNzctZmUzZjEwYjU5NGNiLDE2OTEwMDIzMDkzMTgiLCJzdWJqZWN0Ijoic2VhbGlnaHRzX21vbml0b3JAYWdlbnQiLCJhdWRpZW5jZSI6WyJhZ2VudHMiXSwieC1zbC1yb2xlIjoiYWdlbnQiLCJ4LXNsLXNlcnZlciI6Imh0dHBzOi8vdHV0b3JpYWwuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTEwMDIzMDl9.PPpTPq4cHdX3J6e9TPkaLzJ-9l3ZvPHVjxch4Wfs1alBY7PlZSggi6nEaDcyzEp13FIi9_LT_qecJs7wzkmT4bNYxLqTSc773Btifo3_R22VdcDOq-RtXlU3CsR9fNXg1jHbwhkeQEsefT2Xly0vtxT0bqXjipLlCT6DwldR-9yagZA5x98JNGRCY3Ch9a6jrxRu9AQXMkLAE-2Cxti9IoTCSQPa3Yi_UajPLmHwF0tCcGxAmm03UdcReIF_KjnHdD7uOwvkIx4frzi7a1_AAInnDxMZzMYxRtCEb_MFRIZKQIz43n53aPR6lTZMce4dA00AxKtU-6oHKmteC0KLQYHLs1YhzzoOwmM42EcL2BeSKhIHc4iGsyuSsmroeIU_Mbj1EgkKa1nsnUCdozc2ev4ytRALvQEY9OZcwWKAEndqScZZw8VKPAwKEgvabY9apc2u9BLpqBlh8En3HW5FMwGhVzoYnRYtHnKnaT_ndddQ9RiDPrMeNFnleqjZoOmPIw8QJc_02boytk5eCW1EMSBimV-Eh-EIsMojgpEaF2hCwjSDzvFAYS0ClbM6iUvowyfFp59WkLohBWsgAfHceG4IzEPt1NpDC1czCTJVZMyuCg8VjsSisr0nU7mKvCjyYs9R0Y5AGaGfHK9nbS-WUuWgSvIzGpqzbdkS03mpxl8  --buildsessionidfile ./ --workspacepath ./

RUN ls -l

COPY --from=builder /install /usr/local

# enable gevent support in debugger
ENV GEVENT_SUPPORT=True

ENTRYPOINT locust --host="http://${FRONTEND_ADDR}" --headless -u "${USERS:-10}" 2>&1
