import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Quando('clico no menu Resumo dos recursos', () => {  
  cy.clicar_resumo_dos_recursos()
})

Quando('seleciono o período do quadrimestre {string}', (campo) => {
  cy.selecionar_periodo_resumo_dos_recursos(campo)
})

Quando('seleciono a conta no quadrimestre {string}', (campo) => { 
  cy.selecionar_conta_resumo_dos_recursos(campo)
})

Entao('sistema retorna na tela de resumo', () => {
  cy.validar_filtro_resumo_dos_recursos()
})

When('verifico o card {string} do recurso', (caso) => {
  cy.validar_card_resumo_dos_recursos(caso)
})

When('verifico o saldo de cada recurso', () => {
  cy.validar_saldo_resumo_dos_recursos()
})

Entao('o sistema deve exibir o card na tela Resumo dos recursos', () => {
  cy.validar_filtro_resumo_dos_recursos() 
})

When('verifico o saldo no campo total do recurso', () => {
  cy.verficar_saldo_reprogramado_resumo_dos_recursos()
})

Entao('valida que é igual reprogramado da tela Resumo dos recursos', () => {
})