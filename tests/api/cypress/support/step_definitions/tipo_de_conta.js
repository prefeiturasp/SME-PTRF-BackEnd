import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('clico no botao {string} da tela tipo de conta', function (btn_tipo_conta) {
	cy.clicar_btn_adicionar_tipo_de_conta(btn_tipo_conta)
});

Dado('informo dado nos campos {string}, {string}, {string}, {string}, {string}, {string} e {string}', function (nome_do_tipo_de_conta, nome_do_banco, n_da_agencia, n_da_conta, n_do_cartao, exibir_os_dados_da_conta_somente_leitura, conta_permite_encerramento) {
	cy.informar_dados_tipo_de_conta(nome_do_tipo_de_conta, nome_do_banco, n_da_agencia, n_da_conta, n_do_cartao, exibir_os_dados_da_conta_somente_leitura, conta_permite_encerramento)
});

Dado('clico no botao {string} da tela tipo de conta na tabela com a opcao {string}', function (btn_tipo_conta,nome_tabela_edicao) {
	cy.clicar_btn_adicionar_tipo_de_conta(btn_tipo_conta,nome_tabela_edicao)
});

Dado('sistema apresenta a {string} para afirmacao da exclusao do tipo de conta', function (mensagem_de_confirmacao_de_erro) {
	cy.validar_mensagem_de_exclusao_tipo_de_conta(mensagem_de_confirmacao_de_erro)
});

Dado('informo dados no campo {string} da tela de tipo de conta', function (dados_da_pesquisa) {
	cy.informar_dados_consulta_tipo_conta(dados_da_pesquisa)
});

Dado('sistema retorna dados da consulta com os valores {string}', function (valores_consulta) {
	cy.validar_resultado_da_consulta_tipo_conta(valores_consulta)
});