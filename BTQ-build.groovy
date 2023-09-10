@Library('main-shared-library') _
pipeline{
  agent {
    kubernetes {
      yaml kubernetes.base_pod([
        base_image_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com/sl-jenkins-base-ci:latest",
        ecr_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com",
        shell_memory_request: "2000Mi",
        shell_cpu_request: "1.5",
        shell_memory_limit: "3000Mi",
        shell_cpu_limit: "2.5",
        kaniko_memory_request: "3500Mi",
        kaniko_cpu_request: "1.5",
        kaniko_memory_limit: "4500Mi",
        kaniko_cpu_limit: "2.5",
        kaniko_storage_limit:"6500Mi",
        node_selector: "jenkins"
      ])
      defaultContainer 'shell'
    }
  }
  parameters {
    string(name: 'TAG', defaultValue: '1.2.2', description: 'latest tag')
    string(name: 'BRANCH', defaultValue: 'main', description: 'defult branch')
    //string(name: 'ecr_uri1', defaultValue: '534369319675.dkr.ecr.us-west-2.amazonaws.com/btq', description: 'ecr btq')
    string(name: 'SERVICE', defaultValue: '', description: 'SErvice name to build')
    string(name: 'machine_dns', defaultValue: 'http://DEV-${env.IDENTIFIER}.dev.sealights.co', description: 'machine DNS')
    string(name: 'BUILD_NAME', defaultValue: 'none', description: 'build name')
    string(name: 'SL_TOKEN', defaultValue: 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL0RFVi1pbnRlZ3JhdGlvbi5hdXRoLnNlYWxpZ2h0cy5pby8iLCJqd3RpZCI6IkRFVi1pbnRlZ3JhdGlvbixuZWVkVG9SZW1vdmUsQVBJR1ctYzNiM2IyY2YtYjA1Yy00ZWM2LThjNjYtZTBmZTJiYzIwNzAzLDE2OTI4Nzc3MDM4ODUiLCJzdWJqZWN0IjoiU2VhTGlnaHRzQGFnZW50IiwiYXVkaWVuY2UiOlsiYWdlbnRzIl0sIngtc2wtcm9sZSI6ImFnZW50IiwieC1zbC1zZXJ2ZXIiOiJodHRwczovL2Rldi1pbnRlZ3JhdGlvbi5kZXYuc2VhbGlnaHRzLmNvL2FwaSIsInNsX2ltcGVyX3N1YmplY3QiOiIiLCJpYXQiOjE2OTI4Nzc3MDN9.dORXtjiTVw9vM3u2eO9l2r3f54NwEFPWVnhZnOWqV4_ZA-q2T86X861S6o4G7M371hMnoePRNoWgkjXp9isgEPEHoG_LQ_pvwc66vi5gBy8okjlypKGMTrz-N8bF1LeswguuSDDPIpm0Qq7KSjcm-GZmtO2IhJu4Q6f-tX0otMvvr6_nuwfVReExsT0Mxoyu0ZFs2HHwuIqhu12v1wNUuiTNIxQnGqckLw1qrroTG-qrDa8ydC111ML9C-u4qdS6G0iDsSdrQk9RETe0b1ow1vMXMFZeQ0vBrJDFjMnaCUhU6iid8xjkZG3T6XAI0k5SBRN8R6dtTO45mE638ohJi1_YBQL8hSkHL-8X_QkbRCH6IFqPcku0Wu2AcaRkBKOoiYAowFxnrQgYx5n_FVuTXNwW-s18Gnebd-bTBveCAHQH6CEbnpznXyMNXc15tOVdfp1n3RHLx9YE2lYI3dsTdwUlwNhto4J1Ym3ZOrLW_GZwLzZyIITfmNUOQVspwzsVOioeA48DZNpZhpZUAK5P19v0KY_iyJKxGajWnAUkXbyqc72d7eG5cUsIgv-r_p7fwnO4Rm1FVaZJ4Cpv7b4yf5YHGJ7BADI5Zw6YXuWQ3d9snZfvKOR50KVZGOykqwExYEwBACpN1WSEoIg8No7wTry_xNPmkTYOHbNoWuzyjTo', description: 'build token')
  }
  environment{
    ECR_FULL_NAME = "btq${params.SERVICE}"
    ECR_URI = "534369319675.dkr.ecr.us-west-2.amazonaws.com/${env.ECR_FULL_NAME}"
  }
  stages{
    stage('Init') {
      steps {
        script {
          // Clone the repository with the specified branch
          git branch: params.BRANCH, url: 'https://github.com/Sealights/microservices-demo.git'
          stage("Create ECR repository") {
            def repo_policy = libraryResource 'ci/ecr/repo_policy.json'
            ecr.create_repo([
              artifact_name: "${env.ECR_FULL_NAME}",
              key_type: "KMS"
            ])
            ecr.set_repo_policy([
              artifact_name: "${env.ECR_FULL_NAME}",
              repo_policy: repo_policy
            ])
          }
          stage("Build Docker ${params.SERVICE} Image") {
            container(name: 'kaniko'){
              script {
                def CONTEXT = params.SERVICE == "cartservice" ? "./src/${params.SERVICE}/src" : "./src/${params.SERVICE}"
                def DP = "${CONTEXT}/Dockerfile"
                def D = "${env.ECR_URI}:${params.TAG}"
                def BUILD_NAME = params.BUILD_NAME
                def SL_TOKEN = params.SL_TOKEN
                echo "BUILD_NAME: ${BUILD_NAME}"
                echo "SL_TOKEN: ${SL_TOKEN}"
                sh """
            /kaniko/executor \
            --context ${CONTEXT} \
            --dockerfile ${DP} \
            --destination ${D} \
            --build-arg BUILD_NAME=${BUILD_NAME} \
            --build-arg SEALIGHTS_TOKEN=${SL_TOKEN}
        """
              }
            }
          }
        }
      }
    }
  }
}
