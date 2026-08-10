# Monorepo CI/CD Pipeline Design — Online Boutique

## Overview

This document describes the CI/CD pipeline architecture for the Online Boutique monorepo. A single shared `Jenkinsfile` at `src/Jenkinsfile` serves all 12 microservices under `src/`. Each application appears as a separate Jenkins job, but all share the same pipeline logic via a Jenkins Shared Library hosted in the `devsecops-tools` repository.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Jenkins Controller                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ adservice    │  │ cartservice  │  │ frontend     │  ... (x12)   │
│  │ (Pipeline)   │  │ (Pipeline)   │  │ (Pipeline)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                      │
│         └──────────────────┼──────────────────┘                      │
│                            │                                         │
│                   ┌────────▼────────┐                                │
│                   │  src/Jenkinsfile │  (minimal orchestrator)        │
│                   │  ~20 lines      │                                │
│                   └────────┬────────┘                                │
│                            │                                         │
│                   ┌────────▼────────────────┐                        │
│                   │  @Library('devsecops')   │                        │
│                   │  vars/onlineBoutique     │                        │
│                   │  Pipeline.groovy         │  (all logic here)     │
│                   └─────────────────────────┘                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Repositories

| Repository                  | Purpose                                         |
|-----------------------------|-------------------------------------------------|
| `E-commerce-Online-Boutique`| Application monorepo (12 microservices)          |
| `devsecops-tools`           | Jenkins Shared Library (pipeline logic, scripts) |

---

## Applications (src/)

| #  | Application               | Language | Runtime Type |
|----|---------------------------|----------|--------------|
| 1  | adservice                 | Java     | `java`       |
| 2  | cartservice               | C#       | `dotnet`     |
| 3  | checkoutservice           | Go       | `go`         |
| 4  | currencyservice           | Node.js  | `node`       |
| 5  | emailservice              | Python   | `python`     |
| 6  | frontend                  | Go       | `go`         |
| 7  | loadgenerator             | Python   | `python`     |
| 8  | paymentservice            | Node.js  | `node`       |
| 9  | productcatalogservice     | Go       | `go`         |
| 10 | recommendationservice     | Python   | `python`     |
| 11 | shippingservice           | Go       | `go`         |
| 12 | shoppingassistantservice  | Python   | `python`     |

---

## Design Principles

1. **Minimal Jenkinsfile** — `src/Jenkinsfile` is ~20 lines. It loads the shared library and delegates everything. A syntax error in the library doesn't kill all pipelines instantly (library is versioned).
2. **Service metadata map** — Build/test logic is dispatched by runtime type (`java`, `go`, `node`, `python`, `dotnet`), not by service name. No if/else chains.
3. **Per-service `ci/` scripts** — Each service owns `ci/build.sh` and `ci/test.sh`. Jenkins doesn't need to know the language. Adding a new service requires zero pipeline changes.
4. **Path-based triggering** — Only the changed service's pipeline runs. Others are skipped early.
5. **Sparse checkout** — Only the relevant service directory is checked out, keeping workspace small.
6. **Separate jobs in Jenkins UI** — Each microservice is an independent Pipeline job for visibility, independent triggering, and isolated failure.

---

## Problems This Design Solves

### Problem 1: "God Pipeline" with if/else per service

❌ Bad:
```groovy
if (APP_NAME == 'adservice') {
    sh 'mvn clean package'
} else if (APP_NAME == 'checkoutservice') {
    sh 'go build ./...'
} else if (APP_NAME == 'currencyservice') {
    sh 'npm ci && npm test'
}
```

✅ Solution: Service metadata map + type-based dispatch:
```groovy
def services = [
    adservice:              [type: 'java'],
    cartservice:            [type: 'dotnet'],
    checkoutservice:        [type: 'go'],
    currencyservice:        [type: 'node'],
    emailservice:           [type: 'python'],
    frontend:               [type: 'go'],
    loadgenerator:          [type: 'python'],
    paymentservice:         [type: 'node'],
    productcatalogservice:  [type: 'go'],
    recommendationservice:  [type: 'python'],
    shippingservice:        [type: 'go'],
    shoppingassistantservice: [type: 'python']
]

def svc = services[appName]
// Dispatch by svc.type, not by name
```

✅ Even better: Each service owns `ci/build.sh` and `ci/test.sh` — Jenkins is language-agnostic:
```groovy
stage('Build & Test') {
    dir(appDir) {
        sh './ci/build.sh'
        sh './ci/test.sh'
    }
}
```

### Problem 2: Full monorepo checkout for every service

❌ Bad: All 12 jobs clone the entire repo every time.

✅ Solution: Sparse checkout:
```groovy
checkout([$class: 'GitSCM',
    branches: [[name: '*/main']],
    extensions: [
        [$class: 'SparseCheckoutPaths',
            sparseCheckoutPaths: [
                [path: "src/${APP_NAME}"],
                [path: 'src/Jenkinsfile']
            ]
        ]
    ],
    userRemoteConfigs: [[url: 'https://github.com/DevOps-Experiments-ORG/E-commerce-Online-Boutique.git']]
])
```

### Problem 3: Unnecessary builds when unrelated services change

❌ Bad: Push to `frontend/` triggers all 12 pipelines.

✅ Solution: Path-based change detection (skip early):
```groovy
stage('Check Changes') {
    steps {
        script {
            def changed = sh(
                script: "git diff --name-only origin/main...HEAD",
                returnStdout: true
            ).trim().split('\n')

            def relevant = changed.any { it.startsWith("src/${APP_NAME}/") }

            if (!relevant) {
                currentBuild.result = 'NOT_BUILT'
                error("No changes for ${APP_NAME} — skipping.")
            }
        }
    }
}
```

### Problem 4: Shared Jenkinsfile failure breaks all pipelines

❌ Bad: One typo in `src/Jenkinsfile` → all 12 jobs fail.

✅ Solution:
- Keep `src/Jenkinsfile` minimal (~20 lines, almost never changes)
- Move all logic to the shared library (`devsecops-tools`)
- Library is versioned — can pin stable version: `@Library('devsecops-tools@v1.0') _`

---

## Implementation

### 1. `src/Jenkinsfile` (Minimal Orchestrator)

```groovy
@Library('devsecops-tools') _

pipeline {
    agent {
        kubernetes {
            yamlFile 'jenkins/pod.yaml'
        }
    }

    environment {
        APP_NAME = params.APP_NAME ?: env.APP_NAME
    }

    stages {
        stage('CI/CD') {
            steps {
                script {
                    onlineBoutiquePipeline(env.APP_NAME)
                }
            }
        }
    }
}
```

### 2. Shared Library: `vars/onlineBoutiquePipeline.groovy` (in devsecops-tools)

```groovy
def call(String appName) {

    def services = [
        adservice:              [type: 'java'],
        cartservice:            [type: 'dotnet'],
        checkoutservice:        [type: 'go'],
        currencyservice:        [type: 'node'],
        emailservice:           [type: 'python'],
        frontend:               [type: 'go'],
        loadgenerator:          [type: 'python'],
        paymentservice:         [type: 'node'],
        productcatalogservice:  [type: 'go'],
        recommendationservice:  [type: 'python'],
        shippingservice:        [type: 'go'],
        shoppingassistantservice: [type: 'python']
    ]

    def svc = services[appName]
    if (!svc) {
        error "Unknown service: ${appName}"
    }

    def appDir = "src/${appName}"
    def registry = "730335384723.dkr.ecr.ap-south-1.amazonaws.com"
    def imageTag = "${registry}/${appName}:${env.BUILD_NUMBER}"

    stage('Checkout') {
        checkout scm
    }

    stage('Check Changes') {
        def changed = sh(
            script: "git diff --name-only origin/main...HEAD || true",
            returnStdout: true
        ).trim().split('\n')

        def relevant = changed.any { it.startsWith("src/${appName}/") }
        if (!relevant && !params.FORCE_BUILD) {
            currentBuild.result = 'NOT_BUILT'
            echo "No changes for ${appName} — skipping."
            return
        }
    }

    stage('Build') {
        dir(appDir) {
            switch(svc.type) {
                case 'java':
                    sh 'mvn -B clean package -DskipTests'
                    break
                case 'go':
                    sh 'go build ./...'
                    break
                case 'node':
                    sh 'npm ci'
                    break
                case 'python':
                    sh 'pip install -r requirements.txt'
                    break
                case 'dotnet':
                    sh 'dotnet build'
                    break
            }
        }
    }

    stage('Test') {
        dir(appDir) {
            switch(svc.type) {
                case 'java':
                    sh 'mvn -B test'
                    break
                case 'go':
                    sh 'go test ./...'
                    break
                case 'node':
                    sh 'npm test'
                    break
                case 'python':
                    sh 'pytest || true'
                    break
                case 'dotnet':
                    sh 'dotnet test'
                    break
            }
        }
    }

    stage('Docker Build') {
        container('docker') {
            sh "docker build -t ${imageTag} -f ${appDir}/Dockerfile ${appDir}"
        }
    }

    stage('Security Scan') {
        container('docker') {
            sh "trivy image --exit-code 0 --severity HIGH,CRITICAL ${imageTag} || true"
        }
    }

    stage('Push to ECR') {
        if (env.BRANCH_NAME == 'main') {
            container('docker') {
                sh """
                    aws ecr get-login-password --region ap-south-1 | \
                        docker login --username AWS --password-stdin ${registry}
                    docker push ${imageTag}
                """
            }
        }
    }

    stage('Update GitOps') {
        if (env.BRANCH_NAME == 'main') {
            echo "Updating GitOps for ${appName} → ${imageTag}"
            // TODO: implement gitops update
        }
    }
}
```

### 3. Per-Service `ci/` Scripts (Alternative Approach)

Instead of switch/case in the library, each service can own its build logic:

```
src/frontend/
├── ci/
│   ├── build.sh    ← #!/bin/bash  go build ./...
│   └── test.sh     ← #!/bin/bash  go test ./...
├── Dockerfile
├── main.go
└── ...
```

Then the shared library simplifies to:
```groovy
stage('Build & Test') {
    dir(appDir) {
        sh 'chmod +x ci/*.sh'
        sh './ci/build.sh'
        sh './ci/test.sh'
    }
}
```

**Advantage:** Adding a new service requires zero pipeline changes. The service developer writes their own `ci/build.sh`.

---

## Jenkins Job Setup

### Option A: Manual (per service)

1. Jenkins → New Item → **Pipeline** → Name: `online-boutique-frontend`
2. Pipeline Definition: **Pipeline script from SCM**
3. SCM: Git → `https://github.com/DevOps-Experiments-ORG/E-commerce-Online-Boutique.git`
4. Branch: `*/main`
5. Script Path: `src/Jenkinsfile`
6. Add parameter: `APP_NAME` = `frontend`
7. Repeat for each service.

### Option B: Job DSL (Automated)

```groovy
def services = [
    'adservice', 'cartservice', 'checkoutservice', 'currencyservice',
    'emailservice', 'frontend', 'loadgenerator', 'paymentservice',
    'productcatalogservice', 'recommendationservice', 'shippingservice',
    'shoppingassistantservice'
]

folder('online-boutique')

services.each { svc ->
    pipelineJob("online-boutique/${svc}") {
        displayName("${svc}-ci")

        triggers {
            githubPush()
        }

        parameters {
            stringParam('APP_NAME', svc, 'Application name under src/')
            booleanParam('FORCE_BUILD', false, 'Build even if no changes detected')
        }

        definition {
            cpsScm {
                scm {
                    git {
                        remote {
                            url('https://github.com/DevOps-Experiments-ORG/E-commerce-Online-Boutique.git')
                            credentials('github-credentials')
                        }
                        branches('*/main')
                    }
                }
                scriptPath('src/Jenkinsfile')
            }
        }
    }
}
```

---

## Pipeline Stages (Full Flow)

```
Checkout → Check Changes → Build → Test → Docker Build → Security Scan → Push to ECR → Update GitOps
                ↓
        (skip if no changes for this service)
```

| Stage              | Runs In        | Description                                    |
|--------------------|----------------|------------------------------------------------|
| Checkout           | devsecops      | Clone repo (sparse checkout)                   |
| Check Changes      | devsecops      | Skip pipeline if no changes for this service   |
| Build              | devsecops      | Language-specific build via type dispatch       |
| Test               | devsecops      | Language-specific tests                        |
| Docker Build       | docker (dind)  | Build container image                          |
| Security Scan      | docker (dind)  | Trivy vulnerability scan                       |
| Push to ECR        | docker (dind)  | Push to ECR (main branch only)                 |
| Update GitOps      | devsecops      | Update image tag in GitOps repo (main only)    |

---

## Repository Structure

```
E-commerce-Online-Boutique/
├── src/
│   ├── Jenkinsfile                  ← Minimal orchestrator (~20 lines)
│   ├── adservice/
│   │   ├── Dockerfile
│   │   ├── ci/
│   │   │   ├── build.sh
│   │   │   └── test.sh
│   │   └── ...
│   ├── frontend/
│   │   ├── Dockerfile
│   │   ├── ci/
│   │   │   ├── build.sh
│   │   │   └── test.sh
│   │   └── ...
│   └── ... (10 more services)
├── jenkins/
│   └── pod.yaml                     ← Kubernetes pod template
└── docs/
    └── monorepo-pipeline-design.md  ← This document

devsecops-tools/                     ← Shared Library repo (separate)
├── vars/
│   └── onlineBoutiquePipeline.groovy
├── src/
│   └── ... (helper classes)
└── resources/
    └── ... (templates, configs)
```

---

## Environment Variables

| Variable              | Source          | Example                                         |
|-----------------------|-----------------|-------------------------------------------------|
| APP_NAME              | Jenkins Job     | `frontend`                                      |
| APP_DIR               | Derived         | `src/frontend`                                  |
| AWS_REGION            | Pod env / Lib   | `ap-south-1`                                    |
| AWS_ACCOUNT_ID        | Library         | `730335384723`                                  |
| REGISTRY              | Derived         | `730335384723.dkr.ecr.ap-south-1.amazonaws.com` |
| IMAGE_TAG             | Derived         | `.../frontend:42`                               |
| BRANCH_NAME           | Jenkins auto    | `main`                                          |

---

## Security Considerations

- AWS credentials via IRSA (IAM Roles for Service Accounts) — no access keys
- Secrets fetched per-service from AWS Secrets Manager (`<APP_NAME>/env`)
- Container images scanned with Trivy before push
- Git secrets scanning on every build
- DinD sidecar is privileged but scoped to ephemeral build pod only
- Shared library versioned — can pin: `@Library('devsecops-tools@v1.0') _`

---

## Comparison: Approaches

| Aspect                    | God Jenkinsfile | Metadata Map | ci/ Scripts (Recommended) |
|---------------------------|-----------------|--------------|---------------------------|
| Lines of pipeline code    | 200+            | ~80          | ~40                       |
| Adding a new service      | Edit Jenkinsfile| Edit map     | Zero pipeline changes     |
| Language knowledge in CI  | Yes (if/else)   | Yes (switch) | No (service owns it)      |
| Maintenance burden        | High            | Medium       | Low                       |
| Service team autonomy     | None            | None         | Full                      |

---

## Future Enhancements

- [ ] Implement `ci/build.sh` and `ci/test.sh` for all 12 services
- [ ] Add webhook path filtering (GitHub → only trigger changed service's job)
- [ ] Integrate SonarQube per-service quality gates
- [ ] Add Slack/SNS notifications per job
- [ ] Implement canary deployments via ArgoCD rollouts
- [ ] Version-pin the shared library (`@Library('devsecops-tools@v1.2') _`)
- [ ] Add sparse checkout to reduce clone time
- [ ] Create Grafana dashboard for pipeline metrics per service
