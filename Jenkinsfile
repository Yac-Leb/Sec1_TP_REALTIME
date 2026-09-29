pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        RUN_INTEGRATION_TESTS = 'true'
        RUN_E2E_TESTS = 'true'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment') {
            steps {
                sh 'python3 --version'
                sh 'docker --version'
            }
        }

        stage('Install') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    docker compose build sales-api
                    docker compose run --no-deps --rm sales-api \
                    pytest tests/unit -v \
                    --cov=app \
                    --cov-report=term-missing
                '''
            }
        }
        stage('Integration Tests') {
            steps {
                sh '''
                    docker run --rm \
                    --network real-time-sales-devops-tp-main_data-platform \
                    -e RUN_INTEGRATION_TESTS=true \
                    -e KAFKA_BOOTSTRAP_SERVERS=kafka:29092 \
                    sales-pipeline-test-sales-api \
                    pytest tests/integration -v
                '''
            }
        }

        stage('Build') {
            steps {
                sh 'docker compose build sales-api spark-streaming'
            }
        }

        stage('E2E Tests') {
            steps {
                sh '''
                    .venv/bin/python -m pytest tests/e2e
                '''
            }
        }

        stage('SonarQube') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }   

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

    }  // ferme stages

    post {
        always {
            junit allowEmptyResults: true, testResults: '**/test-results.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'coverage.xml'
        }
    }
}
