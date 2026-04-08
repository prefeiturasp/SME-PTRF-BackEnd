///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe("Credito Escola - Cadastro", () => {
  it("CT106-Cadastro_de_Credito_Repasse_Valor_Capital", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
