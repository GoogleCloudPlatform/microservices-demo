@Library('main-shared-library') _
pipeline {

  agent {
    kubernetes {
      yaml kubernetes.base_pod([
        base_image_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com/sl-jenkins-base-ci:latest",
        ecr_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com",
        shell_memory_request: "300Mi",
        shell_cpu_request: "0.5",
        shell_memory_limit: "700Mi",
        shell_cpu_limit: "1",
        kaniko_memory_request: "1000Mi",
        kaniko_cpu_request: "2",
        kaniko_memory_limit: "1500Mi",
        kaniko_cpu_limit: "3",
        node_selector: "jenkins"
      ])
      defaultContainer 'shell'
    }
  }

  parameters {
    string(name: 'latest', defaultValue: '', description: 'latest tag')
    string(name: 'branch', defaultValue: 'ahmad-branch', description: 'Branch to clone (ahmad-branch)')
    //string(name: 'ecr_uri1', defaultValue: '534369319675.dkr.ecr.us-west-2.amazonaws.com/btq-', description: 'ecr btq')
  }

  stages {
    stage('Clone Repository') {
      steps {
        script {
          // Clone the repository with the specified branch
          git branch: params.branch, url: 'https://github.com/Sealights/microservices-demo.git'
        }
      }
    }
    //Build parallel images
    stage ('Build BTQ') {
      steps {
        script {
          def parallelLabs = [:]
          //List of all the images name
          def services_list = ["adservice","cartservice","checkoutservice", "currencyservice","emailservice","frontend","paymentservice","productcatalogservice","recommendationservice","shippingservice"]
          //def special_services = ["cartservice"]
          services_list.each { service ->
            parallelLabs["${service}"] = {
              build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"), string(name:'TAG' , value:"1.0.${BUILD_NUMBER}")])
            }
          }
          parallel parallelLabs
        }
      }
    }
  }
}
