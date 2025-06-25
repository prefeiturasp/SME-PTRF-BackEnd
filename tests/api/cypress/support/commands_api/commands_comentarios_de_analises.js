/// <reference types='cypress' />

Cypress.Commands.add('validar_comentarios_de_analises', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/comentarios-de-analises/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('cadastrar_comentarios_de_analises', (body) => {
	cy.request({
		method: 'POST',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/comentarios-de-analises/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('excluir_comentarios_de_analises', (id) => {
	cy.request({
		method: 'DELETE',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/comentarios-de-analises/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('alterar_comentarios_de_analises', (body, id) => {
	cy.request({
		method: 'PUT',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/comentarios-de-analises/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('editar_comentarios_de_analises', (body, id) => {
	cy.request({
		method: 'PATCH',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/comentarios-de-analises/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})
