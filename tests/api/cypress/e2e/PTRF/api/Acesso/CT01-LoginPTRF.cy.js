///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()


describe('Login', () => {

  it('Tela de Login', () => {

    Comum.visitarPaginaPTRF()
    cy.realizar_login('UE')

  })
})
