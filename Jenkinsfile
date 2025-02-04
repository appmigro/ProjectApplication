pipeline {
    agent any

    environment {
        DEPLOY_DIR = "/home/fabunmibukola77/ProjectApplication"
        GUNICORN_SERVICE = "/etc/systemd/system/gunicorn.service"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/appmigro/ProjectApplication.git', branch: 'main', credentialsId: 'github-credentials'
            }
        }

        stage('Fix Permissions') {
            steps {
                sh """
                    sudo mkdir -p ${DEPLOY_DIR}
                    sudo chown -R jenkins:jenkins ${DEPLOY_DIR}
                    sudo chmod -R 755 ${DEPLOY_DIR}
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Run Tests') {
            steps {
                sh """
                    . venv/bin/activate
                    python manage.py test
                """
            }
        }

        stage('Build Artifact') {
            steps {
                sh "tar -czf projectapplication.tar.gz *"
                archiveArtifacts artifacts: 'projectapplication.tar.gz', fingerprint: true
            }
        }

        stage("SonarQube Analysis") {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    script {
                        def scannerHome = tool 'SonarScanner'
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('Upload Artifact To Nexus') {
            steps {
                script {
                    def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def buildNumber = env.BUILD_NUMBER ?: '1'
                    def version = "1.0.${buildNumber}-${commitHash}"

                    nexusArtifactUploader(
                        nexusVersion: 'nexus3',
                        protocol: 'http',
                        nexusUrl: '34.55.243.101:8081',
                        groupId: 'com.appmigro',
                        version: version,
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

        stage('Deploy to Home Directory') {
            steps {
                script {
                    sh """
                        sudo rm -rf ${DEPLOY_DIR}/*
                        sudo tar -xzf projectapplication.tar.gz -C ${DEPLOY_DIR}
                        sudo chown -R jenkins:jenkins ${DEPLOY_DIR}
                    """
                }
            }
        }

        stage('Configure Gunicorn & Nginx') {
            steps {
                script {
                    sh """
                        # Create virtual environment
                        cd ${DEPLOY_DIR}
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt

                        # Setup Gunicorn service
                        echo '[Unit]
                        Description=Gunicorn Daemon for Django
                        After=network.target

                        [Service]
                        User=jenkins
                        Group=jenkins
                        WorkingDirectory=${DEPLOY_DIR}
                        ExecStart=${DEPLOY_DIR}/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock projectapplication.wsgi:application

                        [Install]
                        WantedBy=multi-user.target' | sudo tee ${GUNICORN_SERVICE}

                        # Reload and restart services
                        sudo systemctl daemon-reload
                        sudo systemctl enable gunicorn
                        sudo systemctl restart gunicorn

                        # Configure Nginx
                        echo 'server {
                            listen 80;
                            server_name _;

                            location / {
                                include proxy_params;
                                proxy_pass http://unix:/run/gunicorn.sock;
                            }
                        }' | sudo tee /etc/nginx/sites-available/projectapplication

                        sudo ln -sf /etc/nginx/sites-available/projectapplication /etc/nginx/sites-enabled
                        sudo systemctl restart nginx
                    """
                }
            }
        }
    }
}
