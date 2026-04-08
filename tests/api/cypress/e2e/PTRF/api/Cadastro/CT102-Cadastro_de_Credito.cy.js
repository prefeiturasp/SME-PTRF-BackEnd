
///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe("Credito Escola - Cadastro", () => {
  it("CT102-Cadastro_de_Credito", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
