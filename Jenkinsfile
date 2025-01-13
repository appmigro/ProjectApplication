pipeline {
    agent any
    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'python manage.py test'
            }
        }
        stage('Build Artifact') {
            steps {
                sh 'tar -czf projectapplication.tar.gz *'
                archiveArtifacts artifacts: 'projectapplication.tar.gz', fingerprint: true
            }
          }
        }
    }
}
