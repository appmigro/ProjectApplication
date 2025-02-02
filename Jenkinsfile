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
            agent any
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
                    // def deploy_dir = "/tmp/ProjectApplication/"
                    def deploy_dir = "/home/fabunmibukola77/ProjectApplication/"
                    def nexus_url = "http://34.55.243.101:8081/repository/python_artifacts/com/appmigro/projectapplication"
                    def version = "1.0.${env.BUILD_NUMBER}" // Ensure this matches the Nexus version

                    withCredentials([file(credentialsId: 'gcp-sa-key', variable: 'GCP_KEY')]) {
                        sh """
                            gcloud auth activate-service-account --key-file=$GCP_KEY
                            gcloud config set project ordinal-env-441601-p3

                            # Copy artifact to GCP VM
                            gcloud compute scp projectapplication.tar.gz ${gcp_vm_name}:${deploy_dir} --zone=${gcp_vm_zone}

                            # Deploy on VM
                            gcloud compute ssh ${gcp_vm_name} --zone=${gcp_vm_zone} --command="
                                cd ${deploy_dir}
                                tar -xzf projectapplication.tar.gz
                                source venv/bin/activate
                                pip install -r requirements.txt
                                sudo systemctl restart gunicorn.socket
                            "
                        """
                    }
                }
            }
        }
    }
}
