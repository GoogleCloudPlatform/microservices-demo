// =============================================================================
// onlineBoutiquePipeline.groovy — Shared Library for Online Boutique Monorepo
// =============================================================================
// Location : devsecops-tools/vars/onlineBoutiquePipeline.groovy
// Called by: E-commerce-Online-Boutique/src/Jenkinsfile
// =============================================================================
// COPY THIS FILE TO: devsecops-tools/vars/onlineBoutiquePipeline.groovy
// =============================================================================

def call(Map config = [:]) {

    def appName    = config.appName
    def forceBuild = config.forceBuild ?: false

    // ─── Service Metadata Map ───────────────────────────────────────────────────
    def services = [
        adservice:               [type: 'java'],
        cartservice:             [type: 'dotnet'],
        checkoutservice:         [type: 'go'],
        currencyservice:         [type: 'node'],
        emailservice:            [type: 'python'],
        frontend:                [type: 'go'],
        loadgenerator:           [type: 'python'],
        paymentservice:          [type: 'node'],
        productcatalogservice:   [type: 'go'],
        recommendationservice:   [type: 'python'],
        shippingservice:         [type: 'go'],
        shoppingassistantservice:[type: 'python']
    ]

    // ─── Validate ───────────────────────────────────────────────────────────────
    if (!appName?.trim()) {
        error '''
            APP_NAME is not set. Each Jenkins job must pass APP_NAME
            as a parameter or environment variable.
            Valid: adservice, cartservice, checkoutservice, currencyservice,
            emailservice, frontend, loadgenerator, paymentservice,
            productcatalogservice, recommendationservice, shippingservice,
            shoppingassistantservice
        '''
    }

    def svc = services[appName]
    if (!svc) {
        error "Unknown service: '${appName}'. Check the services map in onlineBoutiquePipeline.groovy"
    }

    // ─── Derived Variables ──────────────────────────────────────────────────────
    def awsRegion    = 'ap-south-1'
    def awsAccountId = '730335384723'
    def registry     = "${awsAccountId}.dkr.ecr.${awsRegion}.amazonaws.com"
    def appDir       = "src/${appName}"
    def imageTag     = "${registry}/${appName}:${env.BUILD_NUMBER}"
    def dockerfile   = "${appDir}/Dockerfile"

    echo """
    ┌──────────────────────────────────────────────┐
    │  Service    : ${appName}
    │  Type       : ${svc.type}
    │  Directory  : ${appDir}
    │  Image      : ${imageTag}
    │  Branch     : ${env.BRANCH_NAME ?: 'unknown'}
    └──────────────────────────────────────────────┘
    """

    // ─── Stage: Checkout ────────────────────────────────────────────────────────
    stage('Checkout') {
        checkout scm
    }

    // ─── Stage: Check Changes (skip if nothing changed for this service) ────────
    stage('Check Changes') {
        if (!forceBuild) {
            def changed = sh(
                script: "git diff --name-only HEAD~1 HEAD || echo 'src/${appName}/'",
                returnStdout: true
            ).trim().split('\n')

            def relevant = changed.any { it.startsWith("src/${appName}/") }

            if (!relevant) {
                echo "No changes detected for ${appName}. Skipping build."
                currentBuild.result = 'NOT_BUILT'
                return
            }
        }
        echo "Changes detected for ${appName}. Proceeding with build."
    }

    // ─── Stage: Build ───────────────────────────────────────────────────────────
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
                    sh 'pip install -r requirements.txt || true'
                    break
                case 'dotnet':
                    sh 'dotnet build'
                    break
                default:
                    echo "No build step defined for type: ${svc.type}"
            }
        }
    }

    // ─── Stage: Test ────────────────────────────────────────────────────────────
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
                    sh 'npm test || true'
                    break
                case 'python':
                    sh 'pytest || python -m pytest || true'
                    break
                case 'dotnet':
                    sh 'dotnet test'
                    break
                default:
                    echo "No test step defined for type: ${svc.type}"
            }
        }
    }

    // ─── Stage: Docker Build ────────────────────────────────────────────────────
    stage('Docker Build') {
        container('docker') {
            sh "docker build -t ${imageTag} -f ${dockerfile} ${appDir}"
        }
    }

    // ─── Stage: Security Scan ───────────────────────────────────────────────────
    stage('Security Scan') {
        container('docker') {
            sh """
                echo "Running Trivy scan on ${imageTag}..."
                trivy image --exit-code 0 --severity HIGH,CRITICAL ${imageTag} || true
            """
        }
    }

    // ─── Stage: Push to ECR (main branch only) ──────────────────────────────────
    stage('Push to ECR') {
        if (env.BRANCH_NAME == 'main') {
            container('docker') {
                sh """
                    apk add --no-cache aws-cli 2>/dev/null || true
                    aws ecr get-login-password --region ${awsRegion} | \
                        docker login --username AWS --password-stdin ${registry}
                    docker push ${imageTag}
                """
            }
            echo "Pushed: ${imageTag}"
        } else {
            echo "Skipping push — not on main branch (current: ${env.BRANCH_NAME})"
        }
    }

    // ─── Stage: Update GitOps ───────────────────────────────────────────────────
    stage('Update GitOps') {
        if (env.BRANCH_NAME == 'main') {
            echo "TODO: Update GitOps repo with image tag ${imageTag} for ${appName}"
            // Implement: clone gitops repo, update values.yaml, push
        } else {
            echo "Skipping GitOps update — not on main branch"
        }
    }
}
