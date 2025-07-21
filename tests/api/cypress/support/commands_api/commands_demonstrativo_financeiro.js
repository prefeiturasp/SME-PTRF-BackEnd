/// <reference types='cypress' />

Cypress.Commands.add('validar_pdf_demonstrativo_financeiro', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/${id}/pdf/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_acoes_demonstrativo_financeiro', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/acoes/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_demonstrativo_financeiro_demonstrativo_info', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/demonstrativo-info/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_demonstrativo_financeiro_documento_final', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/documento-final/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_demonstrativo_financeiro_documento_previa', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/documento-previa/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_demonstrativo_financeiro_previa', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/demonstrativo-financeiro/previa/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})



