///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe("Credito Escola - Cadastro", () => {
  it("CT103-Cadastro_de_Credito_Rendimento_Cheque_Custeio", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
