pipeline {
    environment {
      branchname =  env.BRANCH_NAME.toLowerCase()
      kubeconfig = getKubeconf(env.branchname)
      registryCredential = 'jenkins_registry'
    }
  
    agent {
      node { label 'python-36-ptrf' }
    }

    options {
      buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
      disableConcurrentBuilds()
      skipDefaultCheckout()
    }
  
    stages {
        
        stage('CheckOut') {            
            steps { checkout scm }            
        }

        stage('Preparando BD') {
	  when { branch '_master_' } 
          agent { label 'master' }  
          steps {
            sh '''
                docker run -d --rm --cap-add SYS_TIME --name ptrf-db$BUILD_NUMBER --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=ptrf -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres postgres:14-alpine
               '''
          }
        }
        
        stage('Istalando dependencias') {
          steps {
            sh 'pip install --user pipenv -r requirements/local.txt'
          }
            
        }

        stage('Testes') {
	  when { branch '_master_' } 
          parallel {    
        
            stage('Testes Lint') {
              steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                  sh '''
                    export POSTGRES_HOST=ptrf-db$BUILD_NUMBER
                    python manage.py collectstatic --noinput
                    flake8 --format=pylint --exit-zero --exclude migrations,__pycache__,manage.py,settings.py,.env,__tests__,tests >flake8-output.txt
                    '''
                }
              }
              post {
                success{
                  //Publicando arquivo de relatorio flake8
                  recordIssues(tools: [flake8(pattern: 'flake8-output.txt')])
                }
              }
              
            }
            stage('Testes Unitarios') {
              steps {
                sh '''
                   export POSTGRES_HOST=ptrf-db$BUILD_NUMBER
                   coverage run -m pytest
                   coverage xml
                   '''
              }
              post {
                success{
                  //Publicando arquivo de cobertura
                  publishCoverage adapters: [cobertura('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
                }
              }
            }
          }    
        }

        stage('AnaliseCodigo') {
          steps {
                withSonarQubeEnv('sonarqube-local'){
                  sh 'echo "[ INFO ] Iniciando analise Sonar..." && sonar-scanner \
                  -Dsonar.projectKey=SME-PTRF-BackEnd \
                  -Dsonar.python.coverage.reportPaths=*.xml'
              }
            }
        }

        
        stage('Build') {
          when { anyOf { branch 'master'; branch 'main'; branch "story/*"; branch 'develop'; branch 'release'; branch 'homolog'; branch 'homolog-r2'; branch 'pre-release'; } } 
          steps {
            script {
              imagename1 = "registry.sme.prefeitura.sp.gov.br/${env.branchname}/ptrf-backend"
              //imagename2 = "registry.sme.prefeitura.sp.gov.br/${env.branchname}/sme-outra"
              dockerImage1 = docker.build(imagename1, "-f Dockerfile .")
              //dockerImage2 = docker.build(imagename2, "-f Dockerfile_outro .")
              docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
              dockerImage1.push()
              //dockerImage2.push()
              }
              sh "docker rmi $imagename1"
              //sh "docker rmi $imagename2"
            }
          }
        }
	    
        stage('Deploy'){
            when { anyOf {  branch 'master'; branch 'main'; branch 'development'; branch 'develop'; branch 'release'; branch 'homolog'; branch 'homolog-r2'; branch 'pre-release'; } }        
            steps {
              script{
                if ( env.branchname == 'main' ||  env.branchname == 'master' || env.branchname == 'homolog' || env.branchname == 'release' ) {

			            withCredentials([string(credentialsId: 'aprovadores-ptrf', variable: 'aprovadores')]) {
                    timeout(time: 24, unit: "HOURS") {
                      input message: 'Deseja realizar o deploy?', ok: 'SIM', submitter: "${aprovadores}"
                    }
                  }
                }
                  withCredentials([file(credentialsId: "${kubeconfig}", variable: 'config')]){
                            
                    if ( env.branchname == 'homolog-r2' ) {
                        sh('cp $config '+"$home"+'/.kube/config')
                        sh 'kubectl rollout restart deployment/ptrf-backend -n sme-ptrf-hom2'
                        sh 'kubectl rollout restart deployment/ptrf-celery -n sme-ptrf-hom2'
                        sh 'kubectl rollout restart deployment/ptrf-flower -n sme-ptrf-hom2'
                    }
                    else if( env.branchname == 'pre-release' ){
                        sh('cp $config '+"$home"+'/.kube/config')
                        sh 'kubectl rollout restart deployment/sigescolapre-backend -n sme-sigescola-pre'
                        sh 'kubectl rollout restart deployment/sigescolapre-celery -n sme-sigescola-pre'
                        sh 'kubectl rollout restart deployment/sigescolapre-flower -n sme-sigescola-pre'
                    }
                    else {
                        sh('cp $config '+"$home"+'/.kube/config')
                        sh 'kubectl rollout restart deployment/ptrf-backend -n sme-ptrf'
                        sh 'kubectl rollout restart deployment/ptrf-celery -n sme-ptrf'
                        sh 'kubectl rollout restart deployment/ptrf-flower -n sme-ptrf'
                    }
				          }
                }
              }
            }           
        

        stage('Deploy Ambientes'){
            when { anyOf {  branch 'master'; branch 'main' } }
              parallel {
              stage('Deploy Treino'){          
                steps {
                  sh 'kubectl rollout restart deployment/treinamento-backend -n sigescola-treinamento'
                  sh 'kubectl rollout restart deployment/treinamento-celery -n sigescola-treinamento'
                  sh 'kubectl rollout restart deployment/treinamento-flower -n sigescola-treinamento'	  
                }
              }

              stage('Deploy Treinamento2'){          
                steps {
                  sh 'kubectl rollout restart deployment/treinamento-backend -n sigescola-treinamento2'
                  sh 'kubectl rollout restart deployment/treinamento-celery -n sigescola-treinamento2'
                  sh 'kubectl rollout restart deployment/treinamento-flower -n sigescola-treinamento2'   
                }
              }

            }  
        }                    
      }
      post {
        always{
          //Limpando containers de banco
          sh 'docker rm -f ptrf-db$BUILD_NUMBER'
        }
      }
}

def getKubeconf(branchName) {
    if("main".equals(branchName)) { return "config_prd"; }
    else if ("master".equals(branchName)) { return "config_prd"; }
    else if ("homolog".equals(branchName)) { return "config_hom"; }
    else if ("homolog-r2".equals(branchName)) { return "config_hom"; }
    else if ("release".equals(branchName)) { return "config_hom"; }
    else if ("development".equals(branchName)) { return "config_dev"; }
    else if ("develop".equals(branchName)) { return "config_dev"; }	
    else if ("pre-release".equals(branchName)) { return "config_prd"; }
}
