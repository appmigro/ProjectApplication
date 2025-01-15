pipeline {
    agent any
    triggers {
        githubPush() // Listens for GitHub webhook
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
                nexusArtifactUploader(
                    nexusVersion: 'nexus3',
                    protocol: 'http',
                    nexusUrl: '35.224.113.227:8081',
                    groupId: 'com.appmigro',
                    version: '1.0.0',
                    repository: 'python-artifacts',
                    credentialsId: 'nexus-credentials',
                    artifacts: [[artifactId: 'projectapplication', file: 'projectapplication.tar.gz', type: 'tar.gz']]
                )
            }
        }
    }
}
