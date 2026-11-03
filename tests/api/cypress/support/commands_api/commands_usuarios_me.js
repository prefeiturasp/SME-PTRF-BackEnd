/// <reference types='cypress' />

Cypress.Commands.add('consultar_usuarios_me', (authorization = '') => {
  return cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/usuarios/me/',
    headers: {
      Accept: 'application/json',
      'Accept-Language': 'en',
      Authorization: authorization,
      Cookie: '',
    },
    failOnStatusCode: false,
    retryOnNetworkFailure: false,
    retryOnStatusCodeFailure: false,
    log: false,
  })
})
