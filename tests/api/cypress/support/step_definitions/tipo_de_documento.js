import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('informo dado nos campos {string}, {string},{string},{string},{string}, e {string}  da tela tipo de documento', function (nome_tipo_do_documento,solicitar_a_digitacao_do_numero_do_documento,no_numero_do_documento_deve_constar_apenas_digitos,documento_comprobatorio_de_despesa,habilita_preenchimento_do_imposto,documento_relativo_ao_imposto_recolhido) {
	cy.informar_dados_tipo_de_documento(nome_tipo_do_documento,solicitar_a_digitacao_do_numero_do_documento,no_numero_do_documento_deve_constar_apenas_digitos,documento_comprobatorio_de_despesa,habilita_preenchimento_do_imposto,documento_relativo_ao_imposto_recolhido)
});

Dado('clico no botao {string} da tela tipo de documento', function (botao_tipo_de_documento) {
	cy.clicar_btn_tipo_de_documento(botao_tipo_de_documento)
});

Dado('informo dado nos campos {string} da tela tipo de documento', function (filtrar_por_nome) {
	cy.informar_dados_filtro_por_nome_tipo_de_documento(filtrar_por_nome)
});