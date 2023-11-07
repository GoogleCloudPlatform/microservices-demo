@Library('main-shared-library@ahmad-branch') _
pipeline {
  agent {
    kubernetes {
      yaml kubernetes.base_pod([
        base_image_uri       : "534369319675.dkr.ecr.us-west-2.amazonaws.com/sl-jenkins-base-ci:latest",
        ecr_uri              : "534369319675.dkr.ecr.us-west-2.amazonaws.com",
        shell_memory_request : "5000Mi",
        shell_cpu_request    : "2",
        shell_memory_limit   : "10000Mi",
        shell_cpu_limit      : "5",
        kaniko_memory_request: "1500Mi",
        kaniko_cpu_request   : "2",
        kaniko_memory_limit  : "6000Mi",
        kaniko_cpu_limit     : "5",
        node_selector        : "jenkins"
      ])
      defaultContainer 'shell'
    }
  }

  parameters {
    string(name: 'APP_NAME', defaultValue: 'ahmad-BTQ', description: 'name of the app (integration build)')
    string(name: 'BRANCH', defaultValue: 'ahmad-branch', description: 'Branch to clone (ahmad-branch)')
    string(name: 'CHANGED_BRANCH', defaultValue: 'changed', description: 'Branch to clone (ahmad-branch)')
    string(name: 'BRANCH', defaultValue: 'ahmad-branch', description: 'Branch to clone (ahmad-branch)')
    string(name: 'BUILD_BRANCH', defaultValue: 'ahmad-branch', description: 'Branch to Build images that have the creational LAB_ID (send to ahmad branch to build)')
    string(name: 'SL_TOKEN', defaultValue: '', description: 'sl-token')
    string(name: 'BUILD_NAME', defaultValue: '', description: 'build name')
    string(name: 'JAVA_AGENT_URL', defaultValue: 'https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz', description: 'use different java agent')
    string(name: 'DOTNET_AGENT_URL', defaultValue: 'https://agents.sealights.co/dotnetcore/latest/sealights-dotnet-agent-alpine-self-contained.tar.gz', description: 'use different dotnet agent')
    string(name: 'NODE_AGENT_URL', defaultValue: 'slnodejs', description: 'use different node agent')
    string(name: 'GO_AGENT_URL', defaultValue: 'https://agents.sealights.co/slgoagent/latest/slgoagent-linux-amd64.tar.gz', description: 'use different go agent')
    string(name: 'GO_SLCI_AGENT_URL', defaultValue: 'https://agents.sealights.co/slcli/latest/slcli-linux-amd64.tar.gz', description: 'use different slci go agent')
    string(name: 'PYTHON_AGENT_URL', defaultValue: 'sealights-python-agent', description: 'use different python agent')
    choice(name: 'TEST_TYPE', choices: ['All Tests IN One Image', 'Tests sequential', 'Tests parallel'], description: 'Choose test type')
  }


  environment {
    DEV_INTEGRATION_SL_TOKEN = secrets.get_secret("mgmt/btq_token", "us-west-2")
  }

  stages {
    stage('Clone Repository') {
      steps {
        script {
          boutique.clone_repo(
            branch: params.BRANCH
          )
        }
      }
    }


    //Build parallel images
    stage('Build BTQ') {
      steps {
        script {
          def MapUrl = new HashMap()
          MapUrl.put('JAVA_AGENT_URL', "${params.JAVA_AGENT_URL}")
          MapUrl.put('DOTNET_AGENT_URL', "${params.DOTNET_AGENT_URL}")
          MapUrl.put('NODE_AGENT_URL', "${params.NODE_AGENT_URL}")
          MapUrl.put('GO_AGENT_URL', "${params.GO_AGENT_URL}")
          MapUrl.put('GO_SLCI_AGENT_URL', "${params.GO_SLCI_AGENT_URL}")
          MapUrl.put('PYTHON_AGENT_URL', "${params.PYTHON_AGENT_URL}")

          boutique.build_btq(
            sl_token: params.SL_TOKEN,
            dev_integraion_sl_token: env.DEV_INTEGRATION_SL_TOKEN,
            build_name: params.BUILD_NAME,
            branch: params.BRANCH,
            mapurl: MapUrl
          )
        }
      }
    }

    stage('Spin-Up BTQ') {
      steps {
        script {
          boutique.SpinUpBoutiqeEnvironment(
            IDENTIFIER : params.branch+"-"+env.CURRENT_VERSION,
            branch: params.BRANCH,
            app_name: params.APP_NAME,
            build_branch: params.BUILD_BRANCH,
            java_agent_url: params.JAVA_AGENT_URL,
            dotnet_agent_url: params.DOTNET_AGENT_URL,
            sl_branch : params.BRANCH,
            git_branch : params.BUILD_BRANCH
          )
        }
      }
    }

    stage('Run Tests') {
      steps {
        script {
          boutique.run_tests(
            branch: params.BRANCH,
            test_type: params.TEST_TYPE
          )
        }
      }
    }

    stage('Run Api-Tests Before Changes') {
      steps {
        script {
          boutique.run_api_tests_before_changes(
            branch: params.BRANCH,
            app_name: params.APP_NAME
          )
        }
      }
    }


    stage('Changed - Clone Repository') {
      steps {
        script {


          boutique.clone_repo(
            branch: params.CHANGED_BRANCH
          )
        }
      }
    }

    stage('Changed Build BTQ') {
      steps {
        script {
          def MapUrl = new HashMap()
          MapUrl.put('JAVA_AGENT_URL', "${params.JAVA_AGENT_URL}")
          MapUrl.put('DOTNET_AGENT_URL', "${params.DOTNET_AGENT_URL}")
          MapUrl.put('NODE_AGENT_URL', "${params.NODE_AGENT_URL}")
          MapUrl.put('GO_AGENT_URL', "${params.GO_AGENT_URL}")
          MapUrl.put('GO_SLCI_AGENT_URL', "${params.GO_SLCI_AGENT_URL}")
          MapUrl.put('PYTHON_AGENT_URL', "${params.PYTHON_AGENT_URL}")

          boutique.build_btq(
            sl_token: params.SL_TOKEN,
            dev_integraion_sl_token: env.DEV_INTEGRATION_SL_TOKEN,
            build_name: params.BUILD_NAME,
            branch: params.CHANGED_BRANCH,
            mapurl: MapUrl
          )
        }
      }
    }



    stage('Changed Spin-Up BTQ') {
      steps {
        script {
          boutique.SpinUpBoutiqeEnvironment(
            IDENTIFIER = ${params.CHANGED_BRANCH}-${env.CURRENT_VERSION},
            branch: params.CHANGED_BRANCH,
            git_branch : params.CHANGED_BRANCH,
            app_name: params.APP_NAME,
            build_branch: params.BRANCH,
            java_agent_url: params.JAVA_AGENT_URL,
            dotnet_agent_url: params.DOTNET_AGENT_URL,
            sl_branch : params.BRANCH
          )
        }
      }
    }

    stage('Changed Run Tests') {
      steps {
        script {
          boutique.run_tests(
            branch: params.BRANCH,
            test_type: params.TEST_TYPE
          )
        }
      }
    }


    stage('Run API-Tests After Changes') {
      steps {
        script {
          boutique.run_api_tests_after_changes(
            branch: params.BRANCH,
            app_name: params.APP_NAME
          )
        }
      }
    }
  }

  post {
    success {
      script {
        boutique.success_btq(
          IDENTIFIER : "${params.branch}-${env.CURRENT_VERSION}"
        )
        boutique.success_btq(
          IDENTIFIER : "${params.CHANGED_BRANCH}-${env.CURRENT_VERSION}"
        )
      }
    }
    failure {
      script {
        boutique.failure_btq(
          IDENTIFIER : "${params.branch}-${env.CURRENT_VERSION}"
        )
        boutique.failure_btq(
          IDENTIFIER : "${params.CHANGED_BRANCH}-${env.CURRENT_VERSION}"
        )
      }
    }
  }
}


