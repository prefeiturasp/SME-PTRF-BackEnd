import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Quando('clico na opção Dados da Associação', () => {  
})

Entao('sistema retorna {string} para o campo {string}', (valorEsperado, campo) => {
  cy.validar_dados_da_associacao(campo, valorEsperado)
})

Quando('clico para exportar {string}', (tipoExportacao) => {
  const acoes = {
    'dados da associação': cy.exportar_dados_da_associacao,
    'ficha cadastral da associação': cy.exportar_ficha_cadastral_associacao
  }

  acoes[tipoExportacao]?.()
})

Entao('sistema exporta os dados da associação', () => {
  cy.validar_exportar_dados_da_associacao()
})

Quando('informo {string} e {string}', (nome_associacao, ccm) => {
  cy.informar_dados_da_associacao(nome_associacao, ccm)  
})

Quando('clico no botão "Salvar"', () => {    
  cy.salvar_dados_da_associacao()
})

Entao('sistema retorna a {string}', (mensagem) => {
  cy.validar_editar_dados_da_associacao(mensagem)
})

Entao('sistema retorna o {string}', (alerta) => {
  cy.validar_nome_editar_dados_da_associacao(alerta)
})

Quando('tento editar os campos de leitura', () => {  
})

Entao('não permite a edição', () => {
  cy.validar_campos_bloqueados()
})

Quando('clico no botão "Cancelar"', () => {
  cy.cancelar_edicao_da_associacao()
})

Entao('retorna à visualização sem salvar alterações', () => {  
  cy.validar_cancelar_edicao_da_associacao()
})
