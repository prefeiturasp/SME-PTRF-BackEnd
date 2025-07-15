import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('clico no botao {string} da tela Fornecedores', function (btn_fornecedores) {
	cy.clicar_btn_fornecedores(btn_fornecedores)
});

Dado('informo dado nos campos {string} e {string}', function (nome_do_fornecedor, cpf_cnpj) {
	cy.informar_dados_fornecedores(nome_do_fornecedor, cpf_cnpj)
});

Dado('informo dado nos campos {string} e {string} para pesquisa na tela de Fornecedores', function (nome_do_fornecedor, cpf_cnpj) {
	cy.informar_dados_fornecedores_pesquisa(nome_do_fornecedor, cpf_cnpj)
});

Dado('sistema retorna dados da consulta com os valores {string} e {string} na tela de Fornecedores', function (valores_consulta_nome_fornecedor,valores_consulta_cpf_cnpj) {
	cy.validar_resultado_da_consulta_fornecedores(valores_consulta_nome_fornecedor,valores_consulta_cpf_cnpj)
});

Dado('clico no botao {string} da tela fornecedor na tabela com a opcao {string}', function (btn_tipo_conta,nome_tabela_edicao) {
	cy.clicar_btn_fornecedores(btn_tipo_conta,nome_tabela_edicao)
});