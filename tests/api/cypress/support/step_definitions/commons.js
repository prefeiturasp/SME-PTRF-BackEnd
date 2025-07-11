import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Quando('sistema apresenta a {string} na tela', function (mensagem) {
	cy.validar_mensagens_comuns_do_sistema(mensagem)
});

Dado('sistema apresenta a {string} para afirmacao da exclusao', function (mensagem_de_confirmacao_de_erro) {
	cy.validar_mensagem_de_exclusao(mensagem_de_confirmacao_de_erro)
});

Dado('sistema retorna dados da consulta com os valores {string} na de pesquisa', function (resutado_consulta) {
	cy.validar_resultado_da_consulta(resutado_consulta)
});