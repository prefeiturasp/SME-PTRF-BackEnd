import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Entao('excluo o tipo conta com o nome {string} do banco de dados', (nome) => {
	cy.excluir_tipo_de_conta_db(nome)
});

Dado('crio o tipo conta com o nome {string} do banco de dados', (nome) => {
	cy.criar_tipo_de_conta_db(nome)
});

Entao('excluo o fornecedor com o nome {string} do banco de dados', (nome) => {
	cy.excluir_fornecedores_db(nome)
});

Dado('crio o fornecedor com o nome {string} e {string} no banco de dados', (nome, cpf_cnpj) => {
	cy.criar_fornecedor_db(nome, cpf_cnpj)
});

Dado('excluo o Motivo pagamento antecipado com o nome de motivo {string} do banco de dados', (motivo) => {
	cy.excluir_motivo_pagamento_antecipado_db(motivo)
});

Dado('excluo o Motivo pagamento antecipado com o nome de motivo {string} do banco de dados', (motivo) => {
	cy.excluir_motivo_pagamento_antecipado_db(motivo)
});

Dado('crio o Motivo pagamento antecipado com o nome de motivo {string} do banco de dados', (motivo) => {
	cy.criar_motivo_pagamento_antecipado_db(motivo)
});

Dado('excluo o tipo de documento com o nome de {string} do banco de dados', (nome) => {
	cy.excluir_tipo_do_documento_db(nome)
});

Dado('crio o tipo de documento com o nome de {string} do banco de dados', (nome) => {
	cy.criar_tipo_do_documento_db(nome)
});

Dado('excluo o tipo de transacao com o nome de {string} do banco de dados', (nome) => {
	cy.excluir_tipo_de_transacao_db(nome)
});

Dado('crio o tipo de transacao com o nome de {string} do banco de dados', function (nome) {
	cy.criar_tipo_de_transacao_db(nome)
});
