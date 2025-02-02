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
                    def gcp_vm_ip = "34.56.46.158" // Replace with your actual GCP VM public IP
                    def deploy_dir = "/home/fabunmibukola77/"
                    def nexus_url = "http://34.55.243.101:8081/repository/python_artifacts/com/appmigro/projectapplication"
                    def version = "1.0.${env.BUILD_NUMBER}"  // Ensure this matches the version uploaded

                    // Deploy steps
                    sh """
                        ssh -o StrictHostKeyChecking=no fabunmibukola77@${gcp_vm_ip} << EOF
                            cd ${deploy_dir}
                            wget ${nexus_url}/${version}/projectapplication.tar.gz -O projectapplication.tar.gz
                            tar -xzf projectapplication.tar.gz
                            source venv/bin/activate
                            pip install -r requirements.txt
                            sudo systemctl restart gunicorn.socket
                        EOF
                    """
                }
            }
        }
    }
}
