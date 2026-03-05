import { Given, When, Then, Before } from 'cypress-cucumber-preprocessor/steps'

let token

Before(function () {
  cy.gerar_token().then((token) => {
    cy.wrap(token).as('token')
  })
})

Given('que possuo um token de acesso', function () {
  cy.get('@token').then((token) => {
    expect(token).to.exist
  })
})

Given('que não possuo um token de acesso', function () { })

// Buscar dados das associações
When('envio uma requisição GET no endpoint de associações', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('retorna todos dados das associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

    if (!Array.isArray(response.body)) {
      expect(response.body).to.have.property('results')
      expect(response.body).to.have.property('count')
      expect(response.body).to.have.property('page')
      expect(response.body).to.have.property('page_size')

      if (response.body.links) {
        expect(response.body.links).to.have.property('next')
        expect(response.body.links).to.have.property('previous')
      }
    } else {
      expect(response.body).to.be.an('array')
      expect(response.body.length).to.be.greaterThan(0)
    }
  })
})

// Não buscar dados das associações sem autenticação
When('tento uma requisição GET no endpoint de associações', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não busca dados das associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar dados da associação
When('envio uma requisição GET no endpoint da associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('retorna todos dados da associação com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

    if (Array.isArray(response.body)) {
      expect(response.body).to.be.an('array')
      expect(response.body.length).to.be.greaterThan(0)

      response.body.forEach((item) => {
        expect(item).to.have.property('uuid')
        expect(item).to.have.property('nome')
        expect(item).to.have.property('cnpj')
        expect(item).to.have.property('data_de_encerramento')
        expect(item).to.have.property('unidade')
      })
    } else if (response.body.results) {
      expect(response.body).to.have.property('results')
      expect(response.body).to.have.property('count')
      expect(response.body).to.have.property('page')
      expect(response.body).to.have.property('page_size')

      if (response.body.links) {
        expect(response.body.links).to.have.property('next')
        expect(response.body.links).to.have.property('previous')
      }
    } else { 
      expect(response.body).to.have.property('uuid')
      expect(response.body).to.have.property('nome')
      expect(response.body).to.have.property('cnpj')
      expect(response.body).to.have.property('unidade')
      expect(response.body.unidade).to.have.property('uuid')
      expect(response.body.unidade).to.have.property('codigo_eol')
      expect(response.body.unidade).to.have.property('tipo_unidade')
      expect(response.body.unidade).to.have.property('nome')
      expect(response.body.unidade).to.have.property('sigla')
      expect(response.body.unidade).to.have.property('dre')
      expect(response.body).to.have.property('email')
      expect(response.body).to.have.property('presidente_associacao')
      expect(response.body).to.have.property('periodo_inicial')
    }
  })
})

// Não buscar dados da associação sem autenticação
When('tento uma requisição GET no endpoint da associação', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não busca dados da associação retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar as contas vinculadas
When('envio uma requisição GET no endpoint das contas da associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/contas/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('retorna todos as contas vinculadas com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

    if (Array.isArray(response.body)) {   
      expect(response.body).to.be.an('array')
      expect(response.body.length).to.be.greaterThan(0)

      response.body.forEach((item) => {
        expect(item).to.have.property('uuid')
        expect(item).to.have.property('tipo_conta')
        expect(item.tipo_conta).to.have.property('uuid')
        expect(item.tipo_conta).to.have.property('id')
        expect(item.tipo_conta).to.have.property('nome')
        expect(item.tipo_conta).to.have.property('banco_nome')
        expect(item.tipo_conta).to.have.property('agencia')
        expect(item.tipo_conta).to.have.property('numero_conta')
        expect(item.tipo_conta).to.have.property('numero_cartao')
        expect(item.tipo_conta).to.have.property('apenas_leitura')
        expect(item.tipo_conta).to.have.property('permite_inativacao')
        expect(item.tipo_conta).to.have.property('recurso')

        expect(item).to.have.property('banco_nome')
        expect(item).to.have.property('agencia')
        expect(item).to.have.property('numero_conta')
        expect(item).to.have.property('solicitacao_encerramento')
        expect(item).to.have.property('saldo_atual_conta')
        expect(item).to.have.property('habilitar_solicitar_encerramento')
        expect(item).to.have.property('nome')
        expect(item).to.have.property('nome_recurso')
        expect(item).to.have.property('status')
        expect(item).to.have.property('periodo_encerramento_conta')
        expect(item).to.have.property('mostrar_alerta_valores_reprogramados_ao_solicitar')
      })
    } else if (response.body.results) {
      expect(response.body).to.have.property('results')
      expect(response.body).to.have.property('count')
      expect(response.body).to.have.property('page')
      expect(response.body).to.have.property('page_size')

      if (response.body.links) {
        expect(response.body.links).to.have.property('next')
        expect(response.body.links).to.have.property('previous')
      }
    } else {
      expect(response.body).to.have.property('uuid')
      expect(response.body).to.have.property('tipo_conta')
      expect(response.body).to.have.property('banco_nome')
      expect(response.body).to.have.property('agencia')
      expect(response.body).to.have.property('numero_conta')
      expect(response.body).to.have.property('saldo_atual_conta')
      expect(response.body).to.have.property('status')
    }
  })
})

// Não buscar as contas vinculadas sem autenticação
When('tento uma requisição GET no endpoint das contas da associação', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/contas/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não busca as contas vinculadas retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar as contas encerradas da associação
When('envio uma requisição GET nas contas encerradas', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/contas/encerradas',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('retorna as contas encerradas da associação com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Não buscar as contas encerradas sem associação
When('envio uma requisição GET em contas encerradas', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes//contas/encerradas',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('não busca as contas encerradas sem associação', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não buscar as contas encerradas da associação sem autenticação
When('tento uma requisição GET nas contas encerradas', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/contas/encerradas',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não busca as contas encerradas da associação retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Exportar dados da associação
When('envio uma requisição GET para exportar associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/exportar/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('exportar dados da associação com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Não exportar dados da associação sem associação
When('envio a requisição GET de exportar sem associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes//exportar/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('não exportar dados da associação', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não exportar dados da associação sem autenticação
When('tento uma requisição GET para exportar associação', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/exportar/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não exportar dados da associação retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Exportar PDF de dados da associação
When('envio uma requisição GET para exportar PDF da associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/exportar/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('exportar dados da associação em PDF com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)
  })
})

// Não exportar PDF de dados da associação sem associação
When('envio a requisição GET de exportar PDF sem associação', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes//exportar/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('não exportar PDF de dados da associação', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(404)
  })
})

// Não exportar PDF de dados da associação sem autenticação
When('tento uma requisição GET para exportar PDF da associação', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/e4184fb0-3e9a-4539-9d0b-5a47f61996fe/exportar/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não exportar PDF de dados da associação retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar associações no EOL
When('envio uma requisição GET no endpoint de associação EOL', function () {
  cy.get('@token').then((token) => {
    cy.request({
      method: 'GET',
      url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/eol/',
      headers: {
        accept: 'application/json',
        Authorization: `JWT ${token}`
      },
      failOnStatusCode: false
    }).as('response')
  })
})

Then('retornar dados da associação no EOL com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400)
  })
})

// Não buscar associações no EOL sem autenticação
When('tento uma requisição GET no endpoint de associação EOL', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/associacoes/eol/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não busca dados da associação no EOL com status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})