pipeline {
    agent any
    triggers {
        githubPush() // Listens for GitHub webhook events
    }
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
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }
        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                python manage.py test
                '''
            }
        }
        stage('Build Artifact') {
            steps {
                sh '''
                tar -czf projectapplication.tar.gz *
                '''
                archiveArtifacts artifacts: 'projectapplication.tar.gz', fingerprint: true
            }
        }
        stage('Upload to Nexus') {
            steps {
                withCredentials([string(credentialsId: 'nexus-credentials', variable: 'NEXUS_TOKEN')]) {
                    sh '''
                    curl -u admin:$NEXUS_TOKEN --upload-file projectapplication.tar.gz \
                    http://35.224.113.227:8081/repository/python-artifacts/projectapplication.tar.gz
                    '''
                }
            }
        }
    }
}
