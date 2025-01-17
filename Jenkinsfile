pipeline {
    agent any

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/appmigro/ProjectApplication.git', branch:'main', credentialsId: 'github-credentials'  
            }
        }
        stage('Install Dependencies') {
            steps {
                sh '''
                    apt install python3.11-venv
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
    }
}
