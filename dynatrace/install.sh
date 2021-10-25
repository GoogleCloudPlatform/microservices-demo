#!/bin/sh

set -e

CLI="kubectl"
SKIP_CERT_CHECK="false"
ENABLE_VOLUME_STORAGE="false"
CONNECTION_NAME=""
CLUSTER_NAME=""
CLUSTER_NAME_REGEX="^[-_a-zA-Z0-9][-_\.a-zA-Z0-9]*$"
CLUSTER_NAME_LENGTH=256

while [ $# -gt 0 ]; do
  case "$1" in
  --api-url)
    API_URL="$2"
    shift 2
    ;;
  --api-token)
    API_TOKEN="$2"
    shift 2
    ;;
  --paas-token)
    PAAS_TOKEN="$2"
    shift 2
    ;;
  --skip-ssl-verification)
    SKIP_CERT_CHECK="true"
    shift
    ;;
  --enable-volume-storage)
    ENABLE_VOLUME_STORAGE="true"
    shift
    ;;
  --cluster-name)
    CLUSTER_NAME="$2"
    shift 2
    ;;
  --openshift)
    CLI="oc"
    shift
    ;;
  *)
    echo "Warning: skipping unsupported option: $1"
    shift
    ;;
  esac
done

if [ -z "$API_URL" ]; then
  echo "Error: api-url not set!"
  exit 1
fi

if [ -z "$API_TOKEN" ]; then
  echo "Error: api-token not set!"
  exit 1
fi

if [ -z "$PAAS_TOKEN" ]; then
  echo "Error: paas-token not set!"
  exit 1
fi

K8S_ENDPOINT="$("${CLI}" config view --minify -o jsonpath='{.clusters[0].cluster.server}')"
if [ -z "$K8S_ENDPOINT" ]; then
  echo "Error: failed to get kubernetes endpoint!"
  exit 1
fi

if [ -n "$CLUSTER_NAME" ]; then
  if ! echo "$CLUSTER_NAME" | grep -Eq "$CLUSTER_NAME_REGEX"; then
    echo "Error: cluster name \"$CLUSTER_NAME\" does not match regex: \"$CLUSTER_NAME_REGEX\""
    exit 1
  fi

  if [ "${#CLUSTER_NAME}" -ge $CLUSTER_NAME_LENGTH ]; then
    echo "Error: cluster name too long: ${#CLUSTER_NAME} >= $CLUSTER_NAME_LENGTH"
    exit 1
  fi
  CONNECTION_NAME="$CLUSTER_NAME"
else
  CONNECTION_NAME="$(echo "${K8S_ENDPOINT}" | awk -F[/:] '{print $4}')"
fi

set -u

checkIfNSExists() {
  if ! "${CLI}" get ns dynatrace >/dev/null 2>&1; then
    if [ "${CLI}" = "kubectl" ]; then
      "${CLI}" create namespace dynatrace
    else
      "${CLI}" adm new-project --node-selector="" dynatrace
    fi
  fi
}

applyDynatraceOperator() {
  if [ "${CLI}" = "kubectl" ]; then
    "${CLI}" apply -f https://github.com/Dynatrace/dynatrace-operator/releases/latest/download/kubernetes.yaml
  else
    "${CLI}" apply -f https://github.com/Dynatrace/dynatrace-operator/releases/latest/download/openshift.yaml
  fi

  "${CLI}" -n dynatrace create secret generic dynakube --from-literal="apiToken=${API_TOKEN}" --from-literal="paasToken=${PAAS_TOKEN}" --dry-run -o yaml | "${CLI}" apply -f -
}

applyDynaKubeCR() {
  if [ -z "$CLUSTER_NAME" ]; then
    cat <<EOF | "${CLI}" apply -f -
apiVersion: dynatrace.com/v1alpha1
kind: DynaKube
metadata:
  name: dynakube
  namespace: dynatrace
spec:
  apiUrl: ${API_URL}
  skipCertCheck: ${SKIP_CERT_CHECK}
  kubernetesMonitoring:
    enabled: true
  routing:
    enabled: true
  classicFullStack:
    enabled: true
    tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/master
      operator: Exists
    env:
    - name: ONEAGENT_ENABLE_VOLUME_STORAGE
      value: "${ENABLE_VOLUME_STORAGE}"
EOF
  else
    cat <<EOF | "${CLI}" apply -f -
apiVersion: dynatrace.com/v1alpha1
kind: DynaKube
metadata:
  name: dynakube
  namespace: dynatrace
spec:
  apiUrl: ${API_URL}
  skipCertCheck: ${SKIP_CERT_CHECK}
  networkZone: ${CLUSTER_NAME}
  kubernetesMonitoring:
    enabled: true
    group: ${CLUSTER_NAME}
  routing:
    enabled: true
    group: ${CLUSTER_NAME}
  classicFullStack:
    enabled: true
    tolerations:
    - effect: NoSchedule
      key: node-role.kubernetes.io/master
      operator: Exists
    env:
    - name: ONEAGENT_ENABLE_VOLUME_STORAGE
      value: "${ENABLE_VOLUME_STORAGE}"
    args:
    - --set-host-group="${CLUSTER_NAME}"
EOF
  fi
}

addK8sConfiguration() {

  K8S_SECRET_NAME="$(for token in $("${CLI}" get sa dynatrace-kubernetes-monitoring -o jsonpath='{.secrets[*].name}' -n dynatrace); do echo "$token"; done | grep -F token)"
  if [ -z "$K8S_SECRET_NAME" ]; then
    echo "Error: failed to get kubernetes-monitoring secret!"
    exit 1
  fi

  K8S_BEARER="$("${CLI}" get secret "${K8S_SECRET_NAME}" -o jsonpath='{.data.token}' -n dynatrace | base64 --decode)"
  if [ -z "$K8S_BEARER" ]; then
    echo "Error: failed to get bearer token!"
    exit 1
  fi

  if "$SKIP_CERT_CHECK" = "true"; then
    CERT_CHECK_API="false"
  else
    CERT_CHECK_API="true"
  fi

  if [ -z "$CLUSTER_NAME" ]; then
    json="$(
      cat <<EOF
{
  "label": "${CONNECTION_NAME}",
  "endpointUrl": "${K8S_ENDPOINT}",
  "eventsFieldSelectors": [
    {
      "label": "Node events",
      "fieldSelector": "involvedObject.kind=Node",
      "active": true
    }
  ],
  "workloadIntegrationEnabled": true,
  "eventsIntegrationEnabled": false,
  "authToken": "${K8S_BEARER}",
  "active": true,
  "certificateCheckEnabled": "${CERT_CHECK_API}"
}
EOF
    )"
  else
    json="$(
      cat <<EOF
{
  "label": "${CLUSTER_NAME}",
  "endpointUrl": "${K8S_ENDPOINT}",
  "eventsFieldSelectors": [
    {
      "label": "Node events",
      "fieldSelector": "involvedObject.kind=Node",
      "active": true
    }
  ],
  "workloadIntegrationEnabled": true,
  "eventsIntegrationEnabled": false,
  "activeGateGroup": "${CLUSTER_NAME}",
  "authToken": "${K8S_BEARER}",
  "active": true,
  "certificateCheckEnabled": "${CERT_CHECK_API}"
}
EOF
    )"
  fi

  response=$(apiRequest "POST" "/config/v1/kubernetes/credentials" "${json}")

  if echo "$response" | grep -Fq "${CONNECTION_NAME}"; then
    echo "Kubernetes monitoring successfully setup."
  else
    echo "Error adding Kubernetes cluster to Dynatrace: $response"
  fi
}

checkForExistingCluster() {
  response=$(apiRequest "GET" "/config/v1/kubernetes/credentials" "")

  if echo "$response" | grep -Fq "\"name\":\"${CONNECTION_NAME}\""; then
    echo "Error: Cluster already exists: ${CONNECTION_NAME}"
    exit 1
  fi
}

checkTokenScopes() {
  jsonAPI="{\"token\": \"${API_TOKEN}\"}"
  jsonPaaS="{\"token\": \"${PAAS_TOKEN}\"}"

  responseAPI=$(apiRequest "POST" "/v1/tokens/lookup" "${jsonAPI}")

  if echo "$responseAPI" | grep -Fq "Authentication failed"; then
    echo "Error: API token authentication failed!"
    exit 1
  fi

  if ! echo "$responseAPI" | grep -Fq "WriteConfig"; then
    echo "Error: API token does not have config write permission!"
    exit 1
  fi

  if ! echo "$responseAPI" | grep -Fq "ReadConfig"; then
    echo "Error: API token does not have config read permission!"
    exit 1
  fi

  responsePaaS=$(apiRequest "POST" "/v1/tokens/lookup" "${jsonPaaS}")

  if echo "$responsePaaS" | grep -Fq "Token does not exist"; then
    echo "Error: PaaS token does not exist!"
    exit 1
  fi
}

apiRequest() {
  method=$1
  url=$2
  json=$3

  if "$SKIP_CERT_CHECK" = "true"; then
    curl_command="curl -k"
  else
    curl_command="curl"
  fi

  response="$(${curl_command} -sS -X ${method} "${API_URL}${url}" \
    -H "accept: application/json; charset=utf-8" \
    -H "Authorization: Api-Token ${API_TOKEN}" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "${json}")"

  echo "$response"
}

####### MAIN #######
printf "\nCheck for token scopes...\n"
checkTokenScopes
printf "\nCheck if cluster already exists...\n"
checkForExistingCluster
printf "\nCreating Dynatrace namespace...\n"
checkIfNSExists
printf "\nApplying Dynatrace Operator...\n"
applyDynatraceOperator
printf "\nApplying DynaKube CustomResource...\n"
applyDynaKubeCR
printf "\nAdding cluster to Dynatrace...\n"
addK8sConfiguration
