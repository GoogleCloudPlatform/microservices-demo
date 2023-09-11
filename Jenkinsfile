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
    string(name: 'LATEST', defaultValue: '', description: 'latest tag')
    string(name: 'BRANCH', defaultValue: 'Wahbi-branch', description: 'Branch to clone (ahmad-branch)')
    string(name: 'JOB_NAME', defaultValue: '', description: 'tests job name ')
    string(name: 'BUILD_BRANCH', defaultValue: 'Wahbi-branch', description: 'Branch to Build images that have the creational LAB_ID (send to wahbi branch to build)')
    string(name: 'SL_TOKEN', defaultValue: '', description: 'sl-token')
    string(name: 'BUILD_NAME', defaultValue: '', description: 'sl-token')
  }

  environment {
    DEV_INTEGRATION_SL_TOKEN = secrets.get_secret("mgmt/btq_token", "us-west-2")
    // DEV_INTEGRATION_LABID = "integ_master_BTQ"
  }

  stages {
    stage('Clone Repository') {
      steps {
        script {
          // Clone the repository with the specified branch
          git branch: params.BRANCH, url: 'https://github.com/Sealights/microservices-demo.git'
        }
      }
    }
    //Build parallel images
    stage ('Build BTQ') {
      steps {
        script {
          env.CURRENT_VERSION = "ahmad"
          def parallelLabs = [:]
          //List of all the images name
          env.TOKEN= "${params.SL_TOKEN}" == "" ? "${env.DEV_INTEGRATION_SL_TOKEN}"  : "${params.SL_TOKEN}"
          def services_list = ["adservice","cartservice","checkoutservice", "currencyservice","emailservice","frontend","paymentservice","productcatalogservice","recommendationservice","shippingservice"]
          //def special_services = ["cartservice"]
          services_list.each { service ->
            parallelLabs["${service}"] = {
              env.BUILD_NAME= "${params.BUILD_NAME}" == "" ? "${service}:${params.BRANCH}-${env.CURRENT_VERSION}" : "${params.BUILD_NAME}"
              build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"), string(name:'TAG' , value:"${env.CURRENT_VERSION}") , string(name:'BRANCH' , value:"${params.BRANCH}"),string(name:'BUILD_NAME' , value:"${env.BUILD_NAME}"), string(name:'SL_TOKEN' , value:"${env.TOKEN}") ])
            }
          }
          parallel parallelLabs
        }
      }
    }

    stage ('Spin-Up BTQ') {
      steps {
        script{
          env.IDENTIFIER = "${params.BRANCH}-${env.CURRENT_VERSION}"
          env.MACHINE_DNS = "http://dev-${env.IDENTIFIER}.dev.sealights.co:8081"
          env.LAB_ID = sealights.create_lab_id(
            token: "${env.TOKEN}",
            machine: "https://dev-integration.dev.sealights.co",
            app: "BTQ",
            branch: "${params.BUILD_BRANCH}",
            test_env: "${env.IDENTIFIER}",
            lab_alias: "${env.IDENTIFIER}",
            cdOnly: true,
          )

          build(job: 'SpinUpBoutiqeEnvironment', parameters: [string(name: 'ENV_TYPE', value: "DEV"), string(name:'IDENTIFIER' , value:"${env.IDENTIFIER}") ,string(name:'CUSTOM_EC2_INSTANCE_TYPE' , value:"t3a.large"),string(name:'GIT_BRANCH' , value:"${params.BRANCH}"),string(name:'BTQ_LAB_ID' , value:"${env.LAB_ID}"),string(name:'BTQ_TOKEN' , value:"${env.TOKEN}"),string(name:'BTQ_VERSION' , value:"${env.CURRENT_VERSION}")])
        }
      }
    }

    stage ('Run Tests') {
      steps {
        script {
          sleep time: 60, unit: 'SECONDS'
          //env.machine_dns = "http://dev-${env.IDENTIFIER}.dev.sealights.co:8081"
          def parallelLabs = [:]
          //List of all the jobs
          def jobs_list = ["BTQ-java-tests(Junit without testNG)" , "BTQ-python-tests(Pytest framework)" , "BTQ-nodejs-tests(Mocha framework)" , "BTQ-dotnet-tests(MS-test framework)" , "BTQ-nodejs-tests(Jest framework)"]
          jobs_list.each { job ->
            parallelLabs["${job}"] = {
              build(job:"${job}", parameters: [string(name: 'BRANCH', value: "${params.BRANCH}"),string(name: 'SL_LABID', value: "${env.LAB_ID}") , string(name:'SL_TOKEN' , value:"${env.TOKEN}") ,string(name:'MACHINE_DNS1' , value:"${env.MACHINE_DNS}")])
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
        build(job: 'TearDownBoutiqeEnvironment', parameters: [string(name: 'ENV_TYPE', value: "DEV"), string(name:'IDENTIFIER' , value:"${env.IDENTIFIER}")])
        slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "good", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open> and TearDownBoutiqeEnvironment)"
      }
    }
    failure {
      script {
        def env_instance_id = sh(returnStdout: true, script: "aws ec2 --region eu-west-1 describe-instances --filters 'Name=tag:Name,Values=EUW-ALLINONE-DEV-${env.IDENTIFIER}' 'Name=instance-state-name,Values=running' | jq -r '.Reservations[].Instances[].InstanceId'")
        sh "aws ec2 --region eu-west-1 stop-instances --instance-ids ${env_instance_id}"
        slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "danger", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open>) and TearDownBoutiqeEnvironment"
      }
    }
  }
}

