pipeline {
    environment {
      branchname =  env.BRANCH_NAME.toLowerCase()
      kubeconfig = getKubeconf(env.branchname)
      registryCredential = 'jenkins_registry'
    }
    agent {
      kubernetes { label 'AGENT' }
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

        stage('Preparando BD') {
	        when { anyOf { branch 'master_'; branch 'develop_'; branch 'homolog-r2_'; branch 'pre-release_'; branch 'atualizarpython_'; branch 'testeptrf' } }
           steps {
	   agent { kubernetes {
                  label 'ptrf'
                  defaultContainer 'postgres'
                }
              }	
          /*steps {
          //  sh '''
          //      docker run -d --rm --cap-add SYS_TIME --name ptrf-db$BUILD_NUMBER$BRANCH_NAME --network python-network -p 5432 -e TZ="America/Sao_Paulo" -e POSTGRES_DB=ptrf -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres postgres:14-alpine
               '''
          }*/
        }
        }

        stage('Istalando dependencias') {
          when { anyOf { branch 'master_'; branch 'develop_'; branch 'homolog-r2_'; branch 'pre-release_'; branch 'atualizarpython_'; branch 'testeptrf' } }
          agent {
      kubernetes { label 'AGENT-PYTHON310' }
    }
          steps {
            checkout scm
            sh 'pip install --user pipenv -r requirements/local.txt'
          }

        }


            stage('Testes Lint') {
              when { anyOf { branch 'master_'; branch 'develop_'; branch 'homolog-r2_'; branch 'pre-release_'; branch 'atualizarpython_'; branch 'testeptrf' } }
              agent {
      kubernetes { label 'AGENT-PYTHON310' }
    }
              steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                  sh '''
                    export POSTGRES_HOST=ptrf-db$BUILD_NUMBER$BRANCH_NAME
                    python manage.py collectstatic --noinput
                    flake8 --format=pylint --exit-zero --exclude migrations,__pycache__,manage.py,settings.py,.env,__tests__,tests --output-file=flake8-output.txt
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
              when { anyOf { branch 'master_'; branch 'develop_'; branch 'homolog-r2_'; branch 'pre-release_'; branch 'atualizarpython_'; branch 'testeptrf' } }
              agent {
      kubernetes { label 'AGENT' }
    }
              steps {
                sh '''
                   export POSTGRES_HOST=ptrf-db$BUILD_NUMBER$BRANCH_NAME
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

def getKubeconf(branchName) {
    if("main".equals(branchName)) { return "config_prd"; }
    //else if ("master".equals(branchName)) { return "config_prd"; }
    //else if ("homolog".equals(branchName)) { return "config_hom"; }
    //else if ("homolog-r2".equals(branchName)) { return "config_hom"; }
    //else if ("release".equals(branchName)) { return "config_hom"; }
    //else if ("development".equals(branchName)) { return "config_dev"; }
    //else if ("develop".equals(branchName)) { return "config_dev"; }
    //else if ("pre-release".equals(branchName)) { return "config_prd"; }
    //else if ("atualizarpython".equals(branchName)) { return "config_prd"; }
    else if ("testeptrf".equals(branchName)) { return "config_dev_"; }	
}
