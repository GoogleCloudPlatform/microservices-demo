# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# https://mcr.microsoft.com/v2/dotnet/sdk/tags/list
FROM mcr.microsoft.com/dotnet/sdk:7.0.306@sha256:94e91c9e8349b4caba454beb630cf05b56ee3a985e6c0c967ce57f5c58537033 as builder
WORKDIR /app
COPY cartservice.csproj .
RUN dotnet restore cartservice.csproj -r linux-x64
COPY . .
RUN dotnet publish cartservice.csproj -p:PublishSingleFile=false -r linux-x64 --self-contained true -p:PublishTrimmed=True -p:TrimMode=Link -c release -o /cartservice --no-restore

# https://mcr.microsoft.com/v2/dotnet/runtime-deps/tags/list
FROM mcr.microsoft.com/dotnet/runtime-deps:7.0
WORKDIR /app

COPY start-app.sh .
RUN ls

RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Sealights - install prereq, agent, token, bsid
# Best practice it to mount a pre-existing sealights directory depending on the environment (test or prod)
RUN mkdir -p /app/sealights/logs
RUN mkdir -p /app/sealights/agent
RUN wget -nv -O sealights-dotnet-agent-linux.tar.gz https://agents.sealights.co/dotnetcore/latest/sealights-dotnet-agent-linux-self-contained.tar.gz
RUn ls
RUN tar -xzf ./sealights-dotnet-agent-linux.tar.gz --directory /app/sealights/agent
COPY sltoken.txt /app/sealights/agent
RUN ls /app/sealights/agent
RUN cat /app/sealights/agent/sltoken.txt
RUN chmod -R 777 /app/sealights

RUN ls
COPY --from=builder /cartservice .
EXPOSE 7070
ENV DOTNET_EnableDiagnostics=0 \
    ASPNETCORE_URLS=http://*:7070
USER 1000
ENTRYPOINT ["sh","start-app.sh","/app/cartservice"]
