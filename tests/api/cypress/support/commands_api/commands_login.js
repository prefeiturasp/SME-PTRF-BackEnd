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
  
Cypress.Commands.add('gerar_token', () => {
  return cy.request({
    method: 'POST',
    url: Cypress.config('baseUrlPTRFHomol') + `api/login`,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: {
      login: Cypress.config('usuario_homol_sme'),
      senha: Cypress.config('senha_homol'),
      suporte: false
    },
    failOnStatusCode: false
  }).then((response) => {
    expect(response.status).to.eq(200)
    return response.body.token || response.body.access
  })
})