/// <reference types='cypress' />

Cypress.Commands.add('validar_contas_associacoes', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('cadastrar_contas_associacoes', (body) => {
	cy.request({
		method: 'POST',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('excluir_contas_associacoes', (id) => {
	cy.request({
		method: 'DELETE',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('alterar_contas_associacoes', (body,id) => {
	cy.request({
		method: 'PUT',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('editar_contas_associacoes', (body,id) => {
	cy.request({
		method: 'PATCH',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_contas_associacoes_filtros', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/contas-associacoes/filtros/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})