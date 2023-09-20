FROM python:3.10.8-slim@sha256:49749648f4426b31b20fca55ad854caa55ff59dc604f2f76b57d814e0a47c181 as base
FROM base as builder

ARG SEALIGHTS_TOKEN=eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL0RFVi1pbnRlZ3JhdGlvbi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IkRFVi1pbnRlZ3JhdGlvbixuZWVkVG9SZW1vdmUsQVBJR1ctYzNiM2IyY2YtYjA1Yy00ZWM2LThjNjYtZTBmZTJiYzIwNzAzLDE2OTI4Nzc3MDM4ODUiLCJzdWJqZWN0IjoiU2VhTGlnaHRzQGFnZW50IiwiYXVkaWVuY2UiOlsiYWdlbnRzIl0sIngtc2wtcm9sZSI6ImFnZW50IiwieC1zbC1zZXJ2ZXIiOiJodHRwczovL2Rldi1pbnRlZ3JhdGlvbi5kZXYuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTI4Nzc3MDN9.dORXtjiTVw9vM3u2eO9l2r3f54NwEFPWVnhZnOWqV4_ZA-q2T86X861S6o4G7M371hMnoePRNoWgkjXp9isgEPEHoG_LQ_pvwc66vi5gBy8okjlypKGMTrz-N8bF1LeswguuSDDPIpm0Qq7KSjcm-GZmtO2IhJu4Q6f-tX0otMvvr6_nuwfVReExsT0Mxoyu0ZFs2HHwuIqhu12v1wNUuiTNIxQnGqckLw1qrroTG-qrDa8ydC111ML9C-u4qdS6G0iDsSdrQk9RETe0b1ow1vMXMFZeQ0vBrJDFjMnaCUhU6iid8xjkZG3T6XAI0k5SBRN8R6dtTO45mE638ohJi1_YBQL8hSkHL-8X_QkbRCH6IFqPcku0Wu2AcaRkBKOoiYAowFxnrQgYx5n_FVuTXNwW-s18Gnebd-bTBveCAHQH6CEbnpznXyMNXc15tOVdfp1n3RHLx9YE2lYI3dsTdwUlwNhto4J1Ym3ZOrLW_GZwLzZyIITfmNUOQVspwzsVOioeA48DZNpZhpZUAK5P19v0KY_iyJKxGajWnAUkXbyqc72d7eG5cUsIgv-r_p7fwnO4Rm1FVaZJ4Cpv7b4yf5YHGJ7BADI5Zw6YXuWQ3d9snZfvKOR50KVZGOykqwExYEwBACpN1WSEoIg8No7wTry_xNPmkTYOHbNoWuzyjTo
ARG BRANCH
ARG BUILD_NAME=0.4.3
ARG AGENT_URL=sealights-python-agent
# Install Git in the base stage
RUN apt-get -qq update \
    && apt-get install -y --no-install-recommends \
        wget g++ git \
    && rm -rf /var/lib/apt/lists/*

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install ${AGENT_URL}
WORKDIR /recommendationservice
COPY . .
RUN sl-python config --appname recommendationservice --branchname ${BRANCH} --buildname ${BUILD_NAME} --workspacepath ./ --token ${SEALIGHTS_TOKEN} --exclude "*grpc*"
RUN sl-python scan --scm none --token ${SEALIGHTS_TOKEN} --exclude grpc

FROM base

ENV PYTHONUNBUFFERED=1
# get packages
RUN pip install sealights-python-agent
COPY --from=builder /usr/local/lib/python3.10/ /usr/local/lib/python3.10/
WORKDIR /recommendationservice
COPY . .
COPY --from=builder /recommendationservice/buildSessionId.txt .
RUN export SL_BUILD_SESSION_ID=`cat buildSessionId.txt`
ENV PORT "8080"
EXPOSE 8080
CMD sl-python run python recommendation_server.py --labid ${SL_LAB_ID} --token ${SL_TOKEN}