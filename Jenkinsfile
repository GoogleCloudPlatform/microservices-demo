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
    string(name: 'JOB_NAME', defaultValue: '', description: 'tests job name ')
    string(name: 'SL_TOKEN', defaultValue: '', description: 'sl-token')
  }

  environment {
      DEV_INTEGRATION_SL_TOKEN = secrets.get_secret("mgmt/btq-token", "us-west-2")
      TOKEN = "${params.SL_TOKEN}" == "" ?  env.DEV_INTEGRATION_SL_TOKEN : ${params.SL_TOKEN}
      DEV_INTEGRATION_LABID = "integ_master_BTQ"
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
        env.CURRENT_VERSION = "1.0.${BUILD_NUMBER}"
          def parallelLabs = [:]
          //List of all the images name
          def services_list = ["adservice","cartservice","checkoutservice", "currencyservice","emailservice","frontend","paymentservice","productcatalogservice","recommendationservice","shippingservice"]
          //def special_services = ["cartservice"]
          services_list.each { service ->
            parallelLabs["${service}"] = {
              build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"), string(name:'TAG' , value:"${params.BUILD_TAG}")])
            }
          }
          parallel parallelLabs
        }
      }
    }

    stage ('Run Tests') {
      steps {
        script {
        env.CURRENT_VERSION = "1.0.${BUILD_NUMBER}"
          def parallelLabs = [:]
          //List of all the images name
          def jobs_list = ["BTQ-java-tests","BTQ-python-tests","BTQ-nodejs-tests","BTQ-dotnet-tests"]
          jobs_list.each { job ->
            parallelLabs["${job}"] = {
              build(job:"${job}", parameters: [string(name: 'branch', value: "ahmad-branch"),string(name: 'SL_LABID', value: "${env.DEV_INTEGRATION_LABID}") , string(name:'SL_TOKEN' , value:"${env.TOKEN}")])
            }
          }
          parallel parallelLabs
        }
      }
    }




  }

  post {
            success {
                script {
                    slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "good", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open>)"
                }
            }
            failure {
                script {
                    slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "danger", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open>)"
                }
            }
        }
}
