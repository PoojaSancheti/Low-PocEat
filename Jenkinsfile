pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'lowpoc-eat'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        KUBECONFIG = credentials('kubeconfig')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Set up Python') {
            steps {
                script {
                    sh 'python -m venv venv'
                    sh 'source venv/bin/activate && pip install -r requirements.txt'
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    sh 'source venv/bin/activate && python manage.py test --no-input'
                }
            }
        }
        
        stage('Run Coverage') {
            steps {
                script {
                    sh '''
                    source venv/bin/activate 
                    pip install coverage
                    coverage run --source='.' manage.py test
                    coverage xml
                    '''
                }
                // Publish coverage report
                publishCoverage(
                    adapters: [coberturaAdapter('coverage.xml')],
                    sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                )
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "--no-cache .")
                }
            }
        }
        
        stage('Run Security Scan') {
            steps {
                script {
                    sh 'pip install bandit safety'
                    sh 'bandit -r . -f xml -o bandit-results.xml || true'
                    sh 'safety check -r requirements.txt --output json > safety-report.json || true'
                }
                // Publish security scan results
                dependencyCheckAnalyzer pattern: '**/dependency-check-report.xml'
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'  // Only deploy from main branch
            }
            steps {
                script {
                    // Apply Kubernetes configuration
                    sh "kubectl apply -f k8s_deployment.yaml"
                    
                    // Update the image in the deployment
                    sh "kubectl set image deployment/lowpoc-eat-deployment lowpoc-eat=${DOCKER_IMAGE}:${DOCKER_TAG} --record"
                    
                    // Check rollout status
                    sh "kubectl rollout status deployment/lowpoc-eat-deployment"
                }
            }
        }
    }
    
    post {
        success {
            echo 'Build and deployment completed successfully!'
        }
        failure {
            echo 'Build or deployment failed!'
            // Send notification
            emailext (
                subject: "FAILED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'",
                body: 'Check console output at ${env.BUILD_URL}console',
                to: 'dev-team@example.com',
                from: 'jenkins@example.com'
            )
        }
        always {
            // Clean up workspace
            cleanWs()
        }
    }
}
