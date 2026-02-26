import * as scriptSQL from '../../fixtures/sql/sql_commands'

Cypress.Commands.add('excluir_tipo_de_conta_db', (nome) => {
	cy.postgreSQL(scriptSQL.delete_tipo_de_conta(nome))
})

Cypress.Commands.add('criar_tipo_de_conta_db', (nome) => {
	cy.postgreSQL(scriptSQL.insert_tipo_de_conta(nome))
})

Cypress.Commands.add('excluir_fornecedores_db', (nome) => {
	cy.postgreSQL(scriptSQL.delete_fornecedores(nome))
})

Cypress.Commands.add('criar_fornecedor_db', (nome, cpf_cnpj) => {
	cy.postgreSQL(scriptSQL.insert_fornecedor(nome, cpf_cnpj))
})

Cypress.Commands.add('excluir_motivo_pagamento_antecipado_db', (motivo) => {
	cy.postgreSQL(scriptSQL.delete_motivo_pagamento_antecipado(motivo))
})

Cypress.Commands.add('criar_motivo_pagamento_antecipado_db', (motivo) => {
	cy.postgreSQL(scriptSQL.insert_motivo_pagamento_antecipado(motivo))
})

Cypress.Commands.add('excluir_tipo_do_documento_db', (nome) => {
	cy.postgreSQL(scriptSQL.delete_tipo_do_documento(nome))
})

Cypress.Commands.add('criar_tipo_do_documento_db', (nome) => {
	cy.postgreSQL(scriptSQL.insert_tipo_do_documento(nome))
})

Cypress.Commands.add('excluir_tipo_de_transacao_db', (nome) => {
	cy.postgreSQL(scriptSQL.delete_tipo_de_transacao(nome))
})

Cypress.Commands.add('criar_tipo_de_transacao_db', (nome) => {
	cy.postgreSQL(scriptSQL.insert_tipo_de_transacao(nome))
})

Cypress.Commands.add('select_dados_das_contas', (associacaoId) => {
	cy.postgreSQL(scriptSQL.select_dados_das_contas(associacaoId))
})

Cypress.Commands.add('select_saldo_recursos_dados_das_contas', (saldos) => {
	cy.postgreSQL(scriptSQL.select_saldo_recursos_dados_das_contas(saldos))
})

Cypress.Commands.add('select_dados_das_contas_associacao', (dados) => {
  return cy.postgreSQL(
    scriptSQL.select_dados_das_contas(dados.associacao_id)
  )
})
