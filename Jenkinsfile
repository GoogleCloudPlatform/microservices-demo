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
                    def services = ['adservice','cartservice','checkoutservice','currencyservice','emailservice','frontend','loadgenerator','paymentservice','productcatalogservice','recommendationservice','shippingservice']
                    services.each { svc ->
                        sh "docker build -t drirahabib/${svc}:latest ./src/${svc}"
                    }
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                echo "Pushing Docker images to Docker Hub..."
                script {
                    def services = ['adservice','cartservice','checkoutservice','currencyservice','emailservice','frontend','loadgenerator','paymentservice','productcatalogservice','recommendationservice','shippingservice']
                    services.each { svc ->
                        sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                        sh "docker push drirahabib/${svc}:latest"
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo "Deploying services to Kubernetes..."
                withCredentials([file(credentialsId: 'kubeconfig-creds', variable: 'KUBECONFIG')]) {
                    sh "kubectl apply -f ./kubernetes-manifests"
                }
            }
        }

        stage('Test Deployment') {
            steps {
                echo "Testing services..."
                sh "kubectl get pods -n default"
                sh "kubectl get svc -n default"
            }
        }

    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully!'
        }
        failure {
            echo 'CI/CD pipeline failed. Check the logs!'
        }
    }
}
