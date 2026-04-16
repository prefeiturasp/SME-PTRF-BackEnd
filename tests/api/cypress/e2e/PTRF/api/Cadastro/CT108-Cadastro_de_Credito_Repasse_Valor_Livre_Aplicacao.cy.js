///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

describe("Credito Escola - Cadastro", () => {
  it("CT108-Cadastro_de_Credito_Repasse_Valor_Livre_Aplicacao", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
