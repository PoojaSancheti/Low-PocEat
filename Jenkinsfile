properties([
  pipelineTriggers([]),
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    command: ["dockerd-entrypoint.sh"]
    args:
      - "--host=tcp://0.0.0.0:2375"
      - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    env:
    - name: DOCKER_TLS_CERTDIR
      value: ""
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    volumeMounts:
    - name: workspace-volume
      mountPath: /home/jenkins/agent

  volumes:
  - name: workspace-volume
    emptyDir: {}
"""
        }
    }

    environment {
        DOCKER_IMAGE = "Low-PocEat"
        SONAR_TOKEN = 'sqp_f42fc7b9e4433f6f08040c3f2303f1e5cc5524c1'
        REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REGISTRY = "${REGISTRY_HOST}/2401173"
        NAMESPACE = "2401173"
        SONAR_PROJECT_KEY = "2401173_Low-PocEat"
    }

    stages {
        stage('Checkout Code') {
            steps {
                deleteDir()
                checkout([$class: 'GitSCM', 
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: 'https://github.com/PoojaSancheti/Low-PocEat.git']]
                ])
                echo "✅ Source code cloned successfully"
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh """
                        docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest .
                        docker image ls
                    """
                }
            }
        }

        stage('Run Tests & Coverage') {
            steps {
                container('dind') {
                    sh """
                        docker run --rm \
                        -v $PWD:/app \
                        -w /app \
                        ${DOCKER_IMAGE}:latest \
                        bash -c "pip install -r requirements.txt && python -m pytest tests/ --cov=./ --cov-report=xml"
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            sonar-scanner \
                            -Dsonar.projectKey= 2401173_Low-PocEat \
                            -Dsonar.projectName= 2401173_Low-PocEat \
                            -Dsonar.host.url=http://localhost:9000 \
                            -Dsonar.token=${SONAR_TOKEN} \
                            -Dsonar.sources=. \
                            -Dsonar.python.coverage.reportPaths=coverage.xml \
                            -Dsonar.sourceEncoding=UTF-8
                        """
                    }
                }
            }
        }

        stage('Push to Nexus') {
            steps {
                container('dind') {
                    withCredentials([usernamePassword(credentialsId: 'nexus-credentials', 
                                                   usernameVariable: 'NEXUS_USER', 
                                                   passwordVariable: 'NEXUS_PASSWORD')]) {
                        sh """
                            docker login ${REGISTRY_HOST} -u ${NEXUS_USER} -p ${NEXUS_PASSWORD}
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker tag ${DOCKER_IMAGE}:${BUILD_NUMBER} ${REGISTRY}/${DOCKER_IMAGE}:latest
                            docker push ${REGISTRY}/${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker push ${REGISTRY}/${DOCKER_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh """
                            # Create namespace if it doesn't exist
                            kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
                            
                            # Deploy application
                            kubectl apply -f deployment.yaml -n ${NAMESPACE}
                            kubectl apply -f service.yaml -n ${NAMESPACE}
                            
                            # Wait for deployment to complete
                            kubectl rollout status deployment/poc-eat-app -n ${NAMESPACE}
                            
                            # Get service URL
                            kubectl get svc -n ${NAMESPACE}
                        """
                    }
                }
            }
        }
    }
    
    post {
        success { 
            echo "✅ Low-PocEat CI/CD Pipeline completed successfully!" 
        }
        failure { 
            echo "❌ Pipeline failed" 
        }
        always { 
            echo "🔄 Cleaning up workspace" 
            cleanWs()
        }
    }
}