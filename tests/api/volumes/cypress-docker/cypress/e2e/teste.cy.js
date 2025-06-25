///<reference types="cypress" />

Cypress.on('uncaught:exception', (err, runnable) => {
  // quando retorna falso previne o  Cypress de falhar o teste
  return false
})
  
describe('PTRF', () => {    
  beforeEach(() => {
    cy.visit('http://ptrf-frontend:80')
  })

  it('Teste', () => {
    
    // redimensionamento da tela
    cy.viewport(1200, 860)
    
    // Login
    cy.get('[id = login]').type("7210418");

    cy.get('[id = senha]').type("Sgp@12345");

    cy.intercept({ method: 'GET', url: '**/api/arquivos-download/quantidade-nao-lidos' }).as('login')
    
    cy.contains('Acessar').click();

    cy.wait('@login').its('response.statusCode').should('eq', 200)

    cy.get('select').select('DRE - SAO MATEUS (DRE)')

    cy.wait(5000)
  })
})  
