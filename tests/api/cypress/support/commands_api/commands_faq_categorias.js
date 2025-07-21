/// <reference types='cypress' />

Cypress.Commands.add('validar_faq_categorias', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/faq-categorias/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('cadastrar_faq_categorias', (body) => {
	cy.request({
		method: 'POST',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/faq-categorias/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('excluir_faq_categorias', (id) => {
	cy.request({
		method: 'DELETE',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/faq-categorias/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('alterar_faq_categorias', (body,id) => {
	cy.request({
		method: 'PUT',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/faq-categorias/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('editar_faq_categorias', (body,id) => {
	cy.request({
		method: 'PATCH',
		url: Cypress.config('baseUrlPTRFHomol') + `/api/faq-categorias/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

