///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe("Credito Escola - Cadastro", () => {
  it("CT107-Cadastro_de_Credito_Repasse_Valor_Custeio", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
