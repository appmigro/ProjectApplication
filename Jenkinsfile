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

        stage("build & SonarQube analysis") {
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
                    // Generate a version dynamically based on the build number or commit hash
                    def commitHash = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def buildNumber = env.BUILD_NUMBER ?: '1'
                    def version = "1.0.${buildNumber}-${commitHash}"

                    nexusArtifactUploader(
                        nexusVersion: 'nexus3',
                        protocol: 'http',
                        nexusUrl: '104.154.93.254:8081',
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

    }
}
