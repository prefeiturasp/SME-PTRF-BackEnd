import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Quando('clico na opção Dados das contas', () => {  
  cy.clicar_dados_das_contas()
})

Entao('sistema retorna na tela de contas {string}', (campo) => {
  cy.validar_preenchimento_dados_das_contas(campo)
})

Quando('clico em dados das contas', () => {
  cy.clicar_dados_das_contas()
})

Quando('clico para exportar na tela de contas {string}', (tipoExportacao) => {
  const acoes = {
    'dados da associação': cy.exportar_dados_das_contas_associacao,
    'ficha cadastral da associação': cy.exportar_ficha_cadastral_dados_das_contas_associacao
  }

  acoes[tipoExportacao]?.()
})

Entao('sistema exporta os dados de contas', () => {
  cy.validar_exportar_dados_das_contas_associacao()
})

Entao('valida na tela dados de contas da associação {string}', (associacaoId) => {
  cy.validar_dados_das_contas_associacao(associacaoId)
})

Entao('o saldo de contas da associação', () => {
  cy.validar_saldo_recursos_dados_das_contas()
})

Quando('carrega os dados das contas', () => {  
  cy.intercept('GET', '**/api/associacoes/*/').as('getAssociacao')

  cy.contains('Dados das contas').click()

  cy.wait('@getAssociacao')
})

Quando('altero o {string} conta da associação', () => {
  cy.alterar_dados_das_contas_associacao()    
})

Entao('sistema altera os dados das contas na tela', () => {
  cy.validar_salvar_dados_das_contas_associacao()   
})

Quando('clico no {string} conta da associação', (campo) => {
  cy.cancelar_edicao_dados_das_contas_associacao(campo)   
})

Entao('sistema não altera os dados das contas na tela', () => {
  cy.validar_cancelar_edicao_dados_das_contas_associacao()   
})

Quando('clico em {string} conta da associação', (botao) => {
  cy.solicitar_encerramento_dados_das_contas_associacao(botao) 
})

Entao('sistema envia a solicitação dos dados das contas', () => {   
})