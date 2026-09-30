/// <reference types='cypress' />

const tokenValido = (token) => {
  if (!token) return false

  try {
    const payloadBase64 = token
      .split('.')[1]
      .replace(/-/g, '+')
      .replace(/_/g, '/')
    const payloadComPadding = payloadBase64.padEnd(
      Math.ceil(payloadBase64.length / 4) * 4,
      '='
    )
    const payload = JSON.parse(atob(payloadComPadding))

    return payload.exp * 1000 > Date.now() + 60000
  } catch (error) {
    return false
  }
}

const solicitarToken = (tentativasRestantes = 2) => {
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
    failOnStatusCode: false,
    log: false
  }).then((response) => {
    const erroTransitorio = [502, 503, 504].includes(response.status)

    if (erroTransitorio && tentativasRestantes > 0) {
      Cypress.log({
        name: 'gerar_token',
        message: `gateway ${response.status}; nova tentativa`,
      })
      return cy
        .wait(2000, { log: false })
        .then(() => solicitarToken(tentativasRestantes - 1))
    }

    expect(response.status).to.eq(200)
    const token = response.body.token || response.body.access

    expect(token).to.exist
    Cypress.env('token_api_sme', token)
    return token
  })
}

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
  const tokenEmCache = Cypress.env('token_api_sme')

  if (tokenValido(tokenEmCache)) {
    return cy.wrap(tokenEmCache, { log: false })
  }

  return solicitarToken()
})
