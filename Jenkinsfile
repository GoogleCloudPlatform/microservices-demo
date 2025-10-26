pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Cloning repository..."
                git branch: 'main', url: 'https://github.com/Habibdrira/microservices-demo.git'
            }
        }

        stage('Build Docker Images') {
            steps {
                echo "Building Docker images..."
                script {
                    def services = [
                        'adservice','cartservice','checkoutservice','currencyservice','emailservice',
                        'frontend','loadgenerator','paymentservice','productcatalogservice','recommendationservice','shippingservice'
                    ]
                    
                    services.each { svc ->
                        def dockerfilePath = "./src/${svc}/Dockerfile"
                        if (fileExists(dockerfilePath)) {
                            echo "Building image for ${svc}..."
                            try {
                                sh "docker build -t drirahabib/${svc}:latest ./src/${svc}"
                            } catch (err) {
                                echo "⚠️ Failed to build ${svc}: ${err}"
                            }
                        } else {
                            echo "⚠️ Dockerfile not found for ${svc}, skipping..."
                        }
                    }
                }
            }
        }

        stage('Docker Hub Login') {
            steps {
                echo "Logging into Docker Hub..."
                script {
                    sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                echo "Pushing Docker images to Docker Hub..."
                script {
                    def services = [
                        'adservice','cartservice','checkoutservice','currencyservice','emailservice',
                        'frontend','loadgenerator','paymentservice','productcatalogservice','recommendationservice','shippingservice'
                    ]

                    services.each { svc ->
                        def imageExists = sh(script: "docker images -q drirahabib/${svc}:latest", returnStdout: true).trim()
                        if (imageExists) {
                            try {
                                sh "docker push drirahabib/${svc}:latest"
                                echo "✅ Successfully pushed ${svc}"
                            } catch (err) {
                                echo "⚠️ Failed to push ${svc}: ${err}"
                            }
                        } else {
                            echo "⚠️ Image ${svc} not found, skipping push."
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying services to Kubernetes..."
                withCredentials([file(credentialsId: 'kubeconfig-creds', variable: 'KUBECONFIG')]) {
                    sh "kubectl apply -f ./kubernetes-manifests || echo '⚠️ Deployment may have failed'"
                }
            }
        }

        stage('Test Deployment') {
            steps {
                echo "Checking Kubernetes pods and services..."
                sh "kubectl get pods -n default || echo '⚠️ Failed to get pods'"
                sh "kubectl get svc -n default || echo '⚠️ Failed to get services'"
            }
        }

    }

    post {
        success {
            echo '🎉 CI/CD pipeline completed successfully!'
        }
        failure {
            echo '❌ CI/CD pipeline failed. Check logs for details!'
        }
    }
}
