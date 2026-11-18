/// <reference types='cypress' />

Cypress.Commands.add('validar_valores_reprogramados', (filtros, recurso_uuid) => {
	return cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + 'api/valores-reprogramados/',
		headers: {
			Authorization: 'JWT ' + globalThis.token,
			'X-Recurso-Selecionado': recurso_uuid,
			Accept: 'application/json',
		},
		qs: filtros,
		timeout: 120000,
		failOnStatusCode: false,
	})
})
