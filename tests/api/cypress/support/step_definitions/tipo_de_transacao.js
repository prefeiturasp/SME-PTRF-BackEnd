import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('clico no botao {string} da tela tipos de transacao', function (btn_tipo_transacao) {
	cy.clicar_btn_adicionar_tipo_de_transacao(btn_tipo_transacao)
});

Dado('informo dado nos campos {string} e {string} da tela tipo de transacao', function (nome_tipo_de_transacao, tem_documento) {
	cy.informar_dados_tipo_de_transacao(nome_tipo_de_transacao, tem_documento)
});

Dado('informo dado nos campos {string} da tela tipo de transacao', function (filtrar_por_nome) {
	cy.informar_dados_filtro_por_nome_tipo_de_transacao(filtrar_por_nome)
});