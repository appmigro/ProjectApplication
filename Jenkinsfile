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
        stage('Upload Artifact To Nexus') {
            steps {
                nexusArtifactUploader(
                    nexusVersion: 'nexus3',
                    protocol: 'http',
                    nexusUrl: '34.31.71.82:8081',
                    groupId: 'com.appmigro',
                    version: '2.0.0',
                    repository: 'python_artifacts',
                    credentialsId: 'nexus-credentials',
                    artifacts: [
                        [
                            artifactId: 'projectapplication',
                            file: "projectapplication.tar.gz",
                            type: 'tar.gz'
                        ]
                    ]
                )
            }
        }
    }
}
