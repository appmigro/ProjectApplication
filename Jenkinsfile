pipeline {
    agent any
    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/appmigro/ProjectApplication.git', branch: 'main', credentialsId: 'github-credentials'
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                source venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
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
