pipeline {
  agent {
    docker {
      image 'python:3.11-slim'
      args '-u root'
    }
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Install dependencies') {
      steps {
        dir('it-tester') {
          sh 'pip install --no-cache-dir -r requirements.txt'
        }
      }
    }
    stage('Run tests') {
      steps {
        dir('it-tester') {
          sh 'python main.py --format all'
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'it-tester/reports/', fingerprint: true, onlyIfSuccessful: false
    }
  }
}
