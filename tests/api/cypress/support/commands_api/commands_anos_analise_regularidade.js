/// <reference types='cypress' />

Cypress.Commands.add('validar_anos_analise_regularidade', (ano) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/anos-analise-regularidade/${ano}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})