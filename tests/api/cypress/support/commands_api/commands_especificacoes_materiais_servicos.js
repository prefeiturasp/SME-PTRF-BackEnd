/// <reference types='cypress' />

Cypress.Commands.add('validar_especificacoes_materiais_servicos', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('cadastrar_especificacoes_materiais_servicos', (body) => {
	cy.request({
		method: 'POST',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('excluir_especificacoes_materiais_servicos', (id) => {
	cy.request({
		method: 'DELETE',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('alterar_especificacoes_materiais_servicos', (body,id) => {
	cy.request({
		method: 'PUT',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('editar_especificacoes_materiais_servicos', (body,id) => {
	cy.request({
		method: 'PATCH',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_tabelas_especificacoes_materiais_servicos', () => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/especificacoes-materiais-servicos/tabelas/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})






