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

Given('que não possuo um token de acesso', function () { 
})

// Buscar as contas das associações 
When('envio uma requisição GET na contas associações', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`
    },
    failOnStatusCode: false
  }).as('response')
})

Then('retorna dados das contas associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('links')
    expect(response.body.links).to.have.property('next')
    expect(response.body.links).to.have.property('previous')

    expect(response.body).to.have.property('count')
    expect(response.body).to.have.property('page')
    expect(response.body).to.have.property('page_size')
    expect(response.body).to.have.property('results')

    const item = response.body.results[0]
    expect(item).to.have.property('id')
    expect(item).to.have.property('uuid')
    expect(item).to.have.property('banco_nome')
    expect(item).to.have.property('agencia')
    expect(item).to.have.property('numero_conta')
    expect(item).to.have.property('numero_cartao')
    expect(item).to.have.property('data_inicio')
    expect(item).to.have.property('associacao')
    expect(item).to.have.property('tipo_conta')
    expect(item).to.have.property('status')

    expect(item).to.have.property('tipo_conta_dados')
    expect(item.tipo_conta_dados).to.have.property('uuid')
    expect(item.tipo_conta_dados).to.have.property('id')
    expect(item.tipo_conta_dados).to.have.property('nome')
    expect(item.tipo_conta_dados).to.have.property('banco_nome')

    expect(item).to.have.property('associacao_dados')
    expect(item.associacao_dados).to.have.property('uuid')
    expect(item.associacao_dados).to.have.property('cnpj')
    expect(item.associacao_dados).to.have.property('email')
    expect(item.associacao_dados).to.have.property('nome')
    expect(item.associacao_dados).to.have.property('unidade')
    expect(item.associacao_dados.unidade).to.have.property('uuid')
    expect(item.associacao_dados.unidade).to.have.property('codigo_eol')
    expect(item.associacao_dados.unidade).to.have.property('dre')
    expect(item.associacao_dados.unidade.dre).to.have.property('uuid')
    expect(item.associacao_dados.unidade.dre).to.have.property('nome')
  })
})

// Não buscar as contas das associações sem autenticação
When('tento a requisição GET na contas associações', function () { 
  return cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },          
    failOnStatusCode: false  
  }).as('response')
})

Then('não busca dados das contas associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Filtrar as contas das associações 
When('envio uma requisição GET no filtro na contas associações', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/filtros/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`
    },
    failOnStatusCode: false
  }).as('response')
})

Then('retorna filtrando dados das contas associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

    expect(response.body).to.have.property('tipos_contas')
    expect(response.body.tipos_contas).to.be.an('array')
    expect(response.body.tipos_contas.length).to.be.greaterThan(0)

  const conta = response.body.tipos_contas[0]
    expect(conta).to.have.property('uuid')
    expect(conta).to.have.property('id')
    expect(conta).to.have.property('nome')
    expect(conta).to.have.property('banco_nome')
    expect(conta).to.have.property('agencia')
    expect(conta).to.have.property('numero_conta')
    expect(conta).to.have.property('apenas_leitura')
    expect(conta).to.have.property('permite_inativacao')
    expect(conta).to.have.property('recurso')
  })
})

// Não filtra as contas das associações sem autenticação
When('tento a requisição GET no filtro de contas associações', function () { 
  return cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/filtros/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },          
    failOnStatusCode: false  
  }).as('response')
})

Then('não filtra dados das contas associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Buscar por id de conta da associações
When('envio uma requisição GET do id de conta das associações', function () {
  cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/369728ef-8a21-4f01-b992-cc314c9a580b',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`
    },
    failOnStatusCode: false
  }).as('response')
})

Then('busca os dados das contas associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

  const item = response.body
    expect(item).to.have.property('id')
    expect(item).to.have.property('uuid')
    expect(item).to.have.property('banco_nome')
    expect(item).to.have.property('agencia')
    expect(item).to.have.property('numero_conta')
    expect(item).to.have.property('numero_cartao')
    expect(item).to.have.property('data_inicio')
    expect(item).to.have.property('associacao')
    expect(item).to.have.property('tipo_conta')
    expect(item).to.have.property('status')
  })
})

// Não buscar por id de conta das associações sem autenticação
When('tento requisição GET do id de conta das associações', function () { 
  return cy.request({
    method: 'GET',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/369728ef-8a21-4f01-b992-cc314c9a580b',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },          
    failOnStatusCode: false  
  }).as('response')
})

Then('não busca os dados das contas associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Alterar por id de conta das associações
When('envio uma requisição PUT do id de conta das associações', function () {
  cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "e4184fb0-3e9a-4539-9d0b-5a47f61996fe",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('altera os dados das contas associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

  const item = response.body
    expect(item).to.have.property('id')
    expect(item).to.have.property('uuid')
    expect(item).to.have.property('banco_nome')
    expect(item).to.have.property('agencia')
    expect(item).to.have.property('numero_conta')
    expect(item).to.have.property('numero_cartao')
    expect(item).to.have.property('data_inicio')
    expect(item).to.have.property('associacao')
    expect(item).to.have.property('tipo_conta')
    expect(item).to.have.property('status')    
  })
})

// Id da associação deve ser informado para alterar conta
When('envio uma requisição PUT sem id de conta das associações', function () {
  cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: " ",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não altera os dados das contas associações com status 400', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Id deve ser obrigatório nas conta das associações
When('envio uma requisição PUT sem id em conta das associações', function () {
  cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não altera os dados das contas associações com método inválido', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Tipo de conta é obrigatório nas conta das associações
When('envio uma requisição PUT sem tipo em conta das associações', function () {
  cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: " ",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não altera os dados das contas associações sem o tipo com status 400', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Status é obrigatório nas conta das associações
When('envio uma requisição PUT sem status em conta das associações', function () {
  cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: " "
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não altera os dados das contas associações sem status', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Não altera por id de conta das associações sem autenticação
When('tento requisição PUT do id de conta das associações', function () { 
  return cy.request({
    method: 'PUT',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },          
    failOnStatusCode: false  
  }).as('response')
})

Then('não altera os dados das contas associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})

// Atualizar por id de conta das associações
When('envio uma requisição PATCH do id de conta das associações', function () {
  cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "e4184fb0-3e9a-4539-9d0b-5a47f61996fe",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('altera os dados das contas associações com status 200', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(200)

  const item = response.body
    expect(item).to.have.property('id')
    expect(item).to.have.property('uuid')
    expect(item).to.have.property('banco_nome')
    expect(item).to.have.property('agencia')
    expect(item).to.have.property('numero_conta')
    expect(item).to.have.property('numero_cartao')
    expect(item).to.have.property('data_inicio')
    expect(item).to.have.property('associacao')
    expect(item).to.have.property('tipo_conta')
    expect(item).to.have.property('status')    
  })
})

// Id da associação deve ser informado para atualizar conta
When('envio uma requisição PATCH sem id de conta das associações', function () {
  cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: " ",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não atualiza os dados das contas associações com status 400', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Id deve ser obrigatório nas conta das associações
When('envio uma requisição PATCH sem id em conta das associações', function () {
  cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não atualiza os dados das contas associações com método inválido', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Tipo de conta é obrigatório nas conta das associações
When('envio uma requisição PATCH sem tipo em conta das associações', function () {
  cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: " ",
      status: "ATIVA"
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não atualiza os dados das contas associações sem o tipo com status 400', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Status é obrigatório nas conta das associações
When('envio uma requisição PATCH sem status em conta das associações', function () {
  cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: `JWT ${this.token}`,
      'Content-Type': 'application/json',
    },
    body: {
      banco_nome: "Banco do Brasil",
      agencia: "1897-X",
      numero_conta: "19.150-7",
      numero_cartao: " ",
      data_inicio: "2020-01-01",
      associacao: "105198f5-1284-4c95-8127-896bf9b09922",
      tipo_conta: "105198f5-1284-4c95-8127-896bf9b09922",
      status: " "
    },
    failOnStatusCode: false
  }).as('response')
})

Then('não atualiza os dados das contas associações sem status', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(400) 
  })
})

// Não altera por id de conta das associações sem autenticação
When('tento requisição PATCH do id de conta das associações', function () { 
  return cy.request({
    method: 'PATCH',
    url: Cypress.config('baseUrlPTRFHomol') + 'api/contas-associacoes/d87a2a26-baee-421e-90cb-b3332a8831f0/',
    headers: {
      accept: 'application/json',
      Authorization: 'JWT token_invalido'
    },          
    failOnStatusCode: false  
  }).as('response')
})

Then('não atualiza os dados das contas associações retornando o status 401', function () {
  cy.get('@response').then((response) => {
    expect(response.status).to.eq(401)
  })
})