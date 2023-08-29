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
    string(name: 'branch', defaultValue: 'Wahbi-branch', description: 'Branch to clone')
    string(name: 'JOB_NAME', defaultValue: '', description: 'tests job name ')
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
                  build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"), string(name:'TAG' , value:"${env.CURRENT_VERSION}"),string(name: 'branch', value: "${params.branch}")])
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
                  build(job:"${job}", parameters: [string(name: 'branch', value: params.branch),string(name: 'SL_LABID', value: "integ_master_BTQ") , string(name:'SL_TOKEN' , value:"eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL0RFVi1pbnRlZ3JhdGlvbi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IkRFVi1pbnRlZ3JhdGlvbixuZWVkVG9SZW1vdmUsQVBJR1ctYzNiM2IyY2YtYjA1Yy00ZWM2LThjNjYtZTBmZTJiYzIwNzAzLDE2OTI4Nzc3MDM4ODUiLCJzdWJqZWN0IjoiU2VhTGlnaHRzQGFnZW50IiwiYXVkaWVuY2UiOlsiYWdlbnRzIl0sIngtc2wtcm9sZSI6ImFnZW50IiwieC1zbC1zZXJ2ZXIiOiJodHRwczovL2Rldi1pbnRlZ3JhdGlvbi5kZXYuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTI4Nzc3MDN9.dORXtjiTVw9vM3u2eO9l2r3f54NwEFPWVnhZnOWqV4_ZA-q2T86X861S6o4G7M371hMnoePRNoWgkjXp9isgEPEHoG_LQ_pvwc66vi5gBy8okjlypKGMTrz-N8bF1LeswguuSDDPIpm0Qq7KSjcm-GZmtO2IhJu4Q6f-tX0otMvvr6_nuwfVReExsT0Mxoyu0ZFs2HHwuIqhu12v1wNUuiTNIxQnGqckLw1qrroTG-qrDa8ydC111ML9C-u4qdS6G0iDsSdrQk9RETe0b1ow1vMXMFZeQ0vBrJDFjMnaCUhU6iid8xjkZG3T6XAI0k5SBRN8R6dtTO45mE638ohJi1_YBQL8hSkHL-8X_QkbRCH6IFqPcku0Wu2AcaRkBKOoiYAowFxnrQgYx5n_FVuTXNwW-s18Gnebd-bTBveCAHQH6CEbnpznXyMNXc15tOVdfp1n3RHLx9YE2lYI3dsTdwUlwNhto4J1Ym3ZOrLW_GZwLzZyIITfmNUOQVspwzsVOioeA48DZNpZhpZUAK5P19v0KY_iyJKxGajWnAUkXbyqc72d7eG5cUsIgv-r_p7fwnO4Rm1FVaZJ4Cpv7b4yf5YHGJ7BADI5Zw6YXuWQ3d9snZfvKOR50KVZGOykqwExYEwBACpN1WSEoIg8No7wTry_xNPmkTYOHbNoWuzyjTo")])
                }
              }
              parallel parallelLabs
            }
          }
        }
    }
  
  post{
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
