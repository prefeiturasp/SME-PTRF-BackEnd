pipeline {
    triggers { cron('30 20 * * 0-5') }

    options {
        buildDiscarder(logRotator(numToKeepStr: '20', artifactNumToKeepStr: '20'))
        disableConcurrentBuilds()
        skipDefaultCheckout()
    }

    agent {
        kubernetes {
            label 'cypress'
            defaultContainer 'cypress-13-6-6'
        }
    }

    environment {
        WORKSPACE_DIR = "${env.WORKSPACE}" // Pega dinamicamente o path correto
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Instalar Dependências') {
            steps {
                script {
                    sh '''
                        rm -rf node_modules package-lock.json
                        npm cache clean --force
                        mkdir -p /home/jenkins/.cache/Cypress
                        chmod -R 777 /home/jenkins/.cache/Cypress
                        wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | tee /etc/apt/trusted.gpg.d/google.asc >/dev/null
                        mkdir -p /usr/share/man/man1/
                        apt update && apt install -y default-jre openjdk-17-jdk zip
                        npm install
                        npm install @shelex/cypress-allure-plugin allure-mocha crypto-js@4.1.1 --save-dev
                    '''
                }
            }
        }

        stage('Executar') {
            steps {
                script {
                    sh '''
                        NO_COLOR=1 npx cypress run \
                            --headless \
                            --spec cypress/e2e/**/* \
                            --reporter mocha-allure-reporter \
                            --browser chrome
                    '''
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                script {
                    sh '''
                        java -version
                        export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
                        export PATH=$JAVA_HOME/bin:/usr/local/bin:$PATH
                        echo "JAVA_HOME=$JAVA_HOME"
                        echo "PATH=$PATH"
                        npm install -g allure-commandline --save-dev
                        chmod -R 777 $WORKSPACE_DIR/allure-results || true
                        allure generate $WORKSPACE_DIR/allure-results --clean --output $WORKSPACE_DIR/allure-report
                        if [ -f $WORKSPACE_DIR/allure-report.zip ]; then
                            rm -f $WORKSPACE_DIR/allure-report.zip
                        fi
                        cd $WORKSPACE_DIR && zip -r allure-results-${BUILD_NUMBER}-$(date +"%d-%m-%Y").zip allure-results
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                sh 'chmod -R 777 $WORKSPACE_DIR'
                if (currentBuild.result == 'SUCCESS' || currentBuild.result == 'FAILURE') {
                    allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                    archiveArtifacts artifacts: 'allure-results-*.zip', fingerprint: true
                }
            }
        }

        success {
            sendTelegram("☑️ Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Success \nLog: \n${env.BUILD_URL}allure")
        }

        unstable {
            sendTelegram("💣 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Unstable \nLog: \n${env.BUILD_URL}allure")
        }

        failure {
            sendTelegram("💥 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Failure \nLog: \n${env.BUILD_URL}allure")
        }

        aborted {
            sendTelegram ("😥 Job Name: ${JOB_NAME} \nBuild: ${BUILD_DISPLAY_NAME} \nStatus: Aborted \nLog: \n${env.BUILD_URL}console")
        }
    }
}

def sendTelegram(message) {
    def encodedMessage = URLEncoder.encode(message, "UTF-8")
    withCredentials([
        string(credentialsId: 'telegramTokensigpae', variable: 'TOKEN'),
        string(credentialsId: 'telegramChatIdsigpae', variable: 'CHAT_ID')
    ]) {
        response = httpRequest (
            consoleLogResponseBody: true,
            contentType: 'APPLICATION_JSON',
            httpMode: 'GET',
            url: "https://api.telegram.org/bot${TOKEN}/sendMessage?text=${encodedMessage}&chat_id=${CHAT_ID}&disable_web_page_preview=true",
            validResponseCodes: '200'
        )
        return response
    }
}
