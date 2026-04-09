///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe('Login', () => {

  it('Tela de Login', () => {

    Comum.visitarPaginaPTRF()
    cy.realizar_login('DRE')

    cy.url({ timeout: 15000 }).should('not.include', 'login')

  })
})