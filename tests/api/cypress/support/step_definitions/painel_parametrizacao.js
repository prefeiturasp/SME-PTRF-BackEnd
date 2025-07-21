import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('clico na opcao {string}', function (opcao_painel_parametrizacao) {
	cy.clicar_opcao_painel_parametrizacao(opcao_painel_parametrizacao)
});

Dado('clico na opcao {string} com a visao SME', function (opcao_menu) {
	cy.clicar_opcao_menu_sme(opcao_menu)
});