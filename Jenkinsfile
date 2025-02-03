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

        stage("Build & SonarQube Analysis") {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    script {
                        def scannerhome = tool 'SonarScanner'
                        sh """
                            ${scannerhome}/bin/sonar-scanner 
                        """   
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

        stage('Deploy to GCP VM') {
            steps {
                script {
                    def gcp_vm_name = "nginx" // Replace with your GCP VM name
                    def gcp_vm_zone = "us-central1-c" // Update with your GCP zone
                    def deploy_dir = "/tmp/ProjectApplication/"
                    def gunicorn_service = "/etc/systemd/system/gunicorn.service"

                    withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY')]) {
                        sh """
                            gcloud auth activate-service-account --key-file=$GCP_KEY
                            gcloud config set project ordinal-env-441601-p3

                            # Copy artifact to GCP VM
                            gcloud compute scp projectapplication.tar.gz ${gcp_vm_name}:${deploy_dir} --zone=${gcp_vm_zone}

                            # Deploy on VM
                            gcloud compute ssh ${gcp_vm_name} --zone=${gcp_vm_zone} --command="
                                # Install dependencies if missing
                                sudo apt update
                                sudo apt install -y python3-pip python3-venv gunicorn nginx

                                # Ensure deployment directory exists
                                sudo mkdir -p ${deploy_dir}
                                sudo chown -R www-data:www-data ${deploy_dir}

                                # Navigate to deploy directory
                                cd ${deploy_dir}

                                # Extract and set up virtual environment
                                tar -xzf projectapplication.tar.gz
                                python3 -m venv venv
                                source venv/bin/activate
                                pip install -r requirements.txt

                                # Set Gunicorn systemd service
                                echo '[Unit]
                                Description=Gunicorn Daemon for Django
                                After=network.target

                                [Service]
                                User=www-data
                                Group=www-data
                                WorkingDirectory=${deploy_dir}
                                ExecStart=${deploy_dir}/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock projectapplication.wsgi:application

                                [Install]
                                WantedBy=multi-user.target' | sudo tee ${gunicorn_service}

                                # Reload and enable Gunicorn service
                                sudo systemctl daemon-reload
                                sudo systemctl enable gunicorn
                                sudo systemctl restart gunicorn

                                # Set Nginx reverse proxy
                                echo 'server {
                                    listen 80;
                                    server_name _;

                                    location / {
                                        include proxy_params;
                                        proxy_pass http://unix:/run/gunicorn.sock;
                                    }
                                }' | sudo tee /etc/nginx/sites-available/projectapplication

                                # Enable Nginx site config
                                sudo ln -sf /etc/nginx/sites-available/projectapplication /etc/nginx/sites-enabled
                                sudo systemctl restart nginx
                            "
                        """
                    }
                }
            }
        }
    }
}
