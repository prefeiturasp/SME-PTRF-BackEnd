/// <reference types='cypress' />

Cypress.Commands.add('autenticar_login', (usuario, senha) => {
	cy.request({
	  method: 'POST',
	  url: Cypress.config('baseUrlPTRFHomol') + `api/login`,
	  body: {
		login: usuario,
		senha: senha,
	  },
	  failOnStatusCode: false
	}).then((responseUserToken) => {
	  globalThis.token =
		responseUserToken.allRequestResponses[0]['Response Body'].access
	})
  })
  