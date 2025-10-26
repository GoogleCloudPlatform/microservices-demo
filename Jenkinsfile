pipeline {
  agent any

  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-id') // Jenkins credentials
  }

  stages {

    stage('Checkout') {
      steps {
        git 'https://github.com/Habibdrira/microservices-demo.git'
      }
    }

    stage('Build Docker Images') {
      steps {
        script {
          sh 'docker build -t drirahabib/adservice:latest ./src/adservice'
          sh 'docker build -t drirahabib/cartservice:latest ./src/cartservice'
          sh 'docker build -t drirahabib/checkoutservice:latest ./src/checkoutservice'
          sh 'docker build -t drirahabib/currencyservice:latest ./src/currencyservice'
          sh 'docker build -t drirahabib/emailservice:latest ./src/emailservice'
          sh 'docker build -t drirahabib/frontend:latest ./src/frontend'
          sh 'docker build -t drirahabib/loadgenerator:latest ./src/loadgenerator'
          sh 'docker build -t drirahabib/paymentservice:latest ./src/paymentservice'
          sh 'docker build -t drirahabib/productcatalogservice:latest ./src/productcatalogservice'
          sh 'docker build -t drirahabib/recommendationservice:latest ./src/recommendationservice'
          sh 'docker build -t drirahabib/shippingservice:latest ./src/shippingservice'
          sh 'docker build -t drirahabib/shoppingassistantservice:latest ./src/shoppingassistantservice'
        }
      }
    }

    stage('Push Docker Images') {
      steps {
        script {
          sh 'docker login -u $DOCKERHUB_CREDENTIALS_USR -p $DOCKERHUB_CREDENTIALS_PSW'
          sh 'docker push drirahabib/adservice:latest'
          sh 'docker push drirahabib/cartservice:latest'
          sh 'docker push drirahabib/checkoutservice:latest'
          sh 'docker push drirahabib/currencyservice:latest'
          sh 'docker push drirahabib/emailservice:latest'
          sh 'docker push drirahabib/frontend:latest'
          sh 'docker push drirahabib/loadgenerator:latest'
          sh 'docker push drirahabib/paymentservice:latest'
          sh 'docker push drirahabib/productcatalogservice:latest'
          sh 'docker push drirahabib/recommendationservice:latest'
          sh 'docker push drirahabib/shippingservice:latest'
          sh 'docker push drirahabib/shoppingassistantservice:latest'
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        script {
          sh 'kubectl apply -f kubernetes-manifests/'
        }
      }
    }

    stage('Test Deployment') {
      steps {
        echo 'Vérifier les pods et services sur Kubernetes'
      }
    }

  }

  post {
    failure {
      echo 'CI/CD pipeline failed. Vérifier les logs !'
    }
  }
}
