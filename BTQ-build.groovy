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
            //List of dockerfiles path
            def dockerfile_path = "${params.SERVICE}" == "cartservice" ? "./src/${params.SERVICE}/src" : "./src/${params.SERVICE}"
            //List of dockerfiles context.
            def dockerfile_context = "${dockerfile_path}/Dockerfile"
            def destinations = [
              "${env.ECR_URI}:-${params.TAG}"
            ]
            container(name: 'kaniko'){
              kaniko.executor([
                context:dockerfile_path,
                dockerfile_path:dockerfile_context,
                destinations:destinations
              ])
            }
          }
        }
      }
    }
  }
}
