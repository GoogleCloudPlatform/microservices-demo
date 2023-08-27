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
    string(name: 'branch', defaultValue: 'Wahbi-branch', description: 'Branch to clone (ahmad-branch)')
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
                  build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"), string(name:'TAG' , value:"Wahbi-${env.CURRENT_VERSION}")])
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
                  build(job:"${job}", parameters: [string(name: 'branch', value: "ahmad-branch"),string(name: 'SL_LABID', value: "integ_main_GoogleMicroserviceDemo") , string(name:'SL_TOKEN' , value:"eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL1BST0QtQ1VTVE9NRVJTMi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IlBST0QtQ1VTVE9NRVJTMixuZWVkVG9SZW1vdmUsQVBJR1ctZDk5MWY3YWMtMDc2MC00OTQ4LWIzNzctZmUzZjEwYjU5NGNiLDE2OTEwMDIzMDkzMTgiLCJzdWJqZWN0Ijoic2VhbGlnaHRzX21vbml0b3JAYWdlbnQiLCJhdWRpZW5jZSI6WyJhZ2VudHMiXSwieC1zbC1yb2xlIjoiYWdlbnQiLCJ4LXNsLXNlcnZlciI6Imh0dHBzOi8vdHV0b3JpYWwuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTEwMDIzMDl9.PPpTPq4cHdX3J6e9TPkaLzJ-9l3ZvPHVjxch4Wfs1alBY7PlZSggi6nEaDcyzEp13FIi9_LT_qecJs7wzkmT4bNYxLqTSc773Btifo3_R22VdcDOq-RtXlU3CsR9fNXg1jHbwhkeQEsefT2Xly0vtxT0bqXjipLlCT6DwldR-9yagZA5x98JNGRCY3Ch9a6jrxRu9AQXMkLAE-2Cxti9IoTCSQPa3Yi_UajPLmHwF0tCcGxAmm03UdcReIF_KjnHdD7uOwvkIx4frzi7a1_AAInnDxMZzMYxRtCEb_MFRIZKQIz43n53aPR6lTZMce4dA00AxKtU-6oHKmteC0KLQYHLs1YhzzoOwmM42EcL2BeSKhIHc4iGsyuSsmroeIU_Mbj1EgkKa1nsnUCdozc2ev4ytRALvQEY9OZcwWKAEndqScZZw8VKPAwKEgvabY9apc2u9BLpqBlh8En3HW5FMwGhVzoYnRYtHnKnaT_ndddQ9RiDPrMeNFnleqjZoOmPIw8QJc_02boytk5eCW1EMSBimV-Eh-EIsMojgpEaF2hCwjSDzvFAYS0ClbM6iUvowyfFp59WkLohBWsgAfHceG4IzEPt1NpDC1czCTJVZMyuCg8VjsSisr0nU7mKvCjyYs9R0Y5AGaGfHK9nbS-WUuWgSvIzGpqzbdkS03mpxl8")])
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
