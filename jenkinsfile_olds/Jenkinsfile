pipeline {
    environment {
      branchname =  env.BRANCH_NAME.toLowerCase()
      kubeconfig = getKubeconf(env.branchname)
      registryCredential = 'jenkins_registry'
      namespace = "${env.branchname == 'develop' ? 'sme-ptrf-dev' : env.branchname == 'homolog' ? 'sme-ptrf-hom' : env.branchname == 'homolog-r2' ? 'sme-ptrf-hom2' : 'sme-ptrf' }"
    }
    agent { kubernetes { 
                  label 'builder'
                  defaultContainer 'builder'
                }
              } 


    options {
      buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '5'))
      disableConcurrentBuilds()
      skipDefaultCheckout()
    }

    stages {

        stage('CheckOut') {
            steps { checkout scm }
        }

        stage('Testes Lint') {
          when { anyOf { branch 'master'; branch 'develop'; branch 'homolog-r2'; branch 'pre-release'; branch 'atualizarpython_'; branch 'homolog_' } }
          agent {
               kubernetes {
                   label 'python311'
                   defaultContainer 'python311'
                }
              }
          steps {
            checkout scm
            sh 'pip install --user pipenv -r requirements/local.txt' //instalação das dependências
	    catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                  sh '''
                    pwd
		    export PATH=$PATH:/root/.local/bin
                    python manage.py collectstatic --noinput
		    flake8 --format=pylint --exit-zero --exclude migrations,__pycache__,manage.py,settings.py,.env,__tests__,tests --output-file=flake8-output.txt
                    '''
                }	  
          }

        }
            stage('Testes Unitarios') {
              when { anyOf { branch 'master'; branch 'develop'; branch 'homolog-r2'; branch 'pre-release'; branch 'atualizarpython_'; branch 'homolog_' } }
              agent {
               kubernetes {
                   label 'python311'
                   defaultContainer 'python311'
                }
              }
              steps {
                   checkout scm
                   sh 'pip install --user pipenv -r requirements/local.txt' //instalação das dependências
                   sh '''
                   export PATH=$PATH:/root/.local/bin
                   python manage.py collectstatic --noinput
		   coverage run -m pytest
                   coverage xml
                   '''
              }
              
            }

        stage('AnaliseCodigo') {
          when { anyOf { branch 'master'; branch 'develop'; branch 'homolog-r2'; branch 'pre-release'; branch 'atualizarpython' } }
          agent { kubernetes { 
                  label 'python311'
                  defaultContainer 'builder'
                }
              } 
          steps {
                withSonarQubeEnv('sonarqube-local'){
                  sh 'echo "[ INFO ] Iniciando analise Sonar..." && sonar-scanner \
                  -Dsonar.projectKey=SME-PTRF-BackEnd \
                  -Dsonar.python.coverage.reportPaths=*.xml'
              }
            }
        }


        stage('Build') {
          when { anyOf { branch 'master'; branch 'main'; branch "story/*"; branch 'develop'; branch 'release'; branch 'homolog'; branch 'homolog-r2'; branch 'pre-release'; branch 'atualizarpython' } }
          steps {
            script {
              imagename1 = "registry.sme.prefeitura.sp.gov.br/${env.branchname}/ptrf-backend"
              dockerImage1 = docker.build(imagename1, "-f Dockerfile .")
              docker.withRegistry( 'https://registry.sme.prefeitura.sp.gov.br', registryCredential ) {
              dockerImage1.push()
              
              }
              sh "docker rmi $imagename1"
               }
          }
        }

        stage('Deploy'){
            when { anyOf {  branch 'master'; branch 'main'; branch 'development'; branch 'develop'; branch 'release'; branch 'homolog'; branch 'homolog-r2'; branch 'pre-release'; branch 'atualizarpython' } }
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
                    if( env.branchname == 'atualizarpython' ){
			                  sh('rm -f '+"$home"+'/.kube/config')
                        sh('cp $config '+"$home"+'/.kube/config')
                        sh 'kubectl rollout restart deployment/sigescolapre-backend -n sme-sigescola-pre'
                        sh 'kubectl rollout restart deployment/sigescolapre-celery -n sme-sigescola-pre'
                        sh 'kubectl rollout restart deployment/sigescolapre-flower -n sme-sigescola-pre'
			                  sh('rm -f '+"$home"+'/.kube/config')
                    } else {
			                  sh('rm -f '+"$home"+'/.kube/config')
                        sh('cp $config '+"$home"+'/.kube/config')
			                  sh "echo ${namespace}"
                        sh "kubectl rollout restart deployment/ptrf-backend -n ${namespace}"
                        sh "kubectl rollout restart deployment/ptrf-celery -n ${namespace}"
                        sh "kubectl rollout restart deployment/ptrf-flower -n ${namespace}"
					    }
                  }
                }
              }
            }

        stage('Deploy Treino'){
              when { anyOf {  branch 'master'; branch 'main' } }
                steps {
                  withCredentials([file(credentialsId: "config_release", variable: 'config')]){
	          sh('rm -f '+"$home"+'/.kube/config')
                  sh('cp $config '+"$home"+'/.kube/config')	
                  sh 'kubectl rollout restart deployment/treinamento-backend -n sme-ptrf-treino'
                  sh 'kubectl rollout restart deployment/treinamento-celery -n sme-ptrf-treino'
                  sh 'kubectl rollout restart deployment/treinamento-flower -n sme-ptrf-treino'
		        sh('rm -f '+"$home"+'/.kube/config')
                }
                }
               }
        stage('Deploy QA'){
              when { anyOf {  branch 'homolog' } }
                steps {
                  withCredentials([file(credentialsId: "config_release", variable: 'config')]){
	          sh('rm -f '+"$home"+'/.kube/config')
                  sh('cp $config '+"$home"+'/.kube/config')	
                  sh 'kubectl rollout restart deployment/qa-backend -n sme-ptrf-qa'
            sh('rm -f '+"$home"+'/.kube/config')
                }
                }
               }
      }
      }

def getKubeconf(branchName) {
    if("main".equals(branchName)) { return "config_prd"; }
    else if ("master".equals(branchName)) { return "config_prd"; }
    else if ("homolog".equals(branchName)) { return "config_release"; }   
    else if ("homolog-r2".equals(branchName)) { return "config_release"; } 
    else if ("release".equals(branchName)) { return "config_release"; }      
    else if ("development".equals(branchName)) { return "config_release"; }    
    else if ("develop".equals(branchName)) { return "config_release"; }    
    else if ("pre-release".equals(branchName)) { return "config_prd"; }
    else if ("atualizarpython".equals(branchName)) { return "config_prd"; }
    }
