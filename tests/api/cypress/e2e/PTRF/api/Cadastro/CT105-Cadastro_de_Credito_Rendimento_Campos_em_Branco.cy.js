///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Gastos = new CreditosEscolaPagina()

describe("Credito Escola - Cadastro", () => {
  it("CT105-Cadastro_de_Credito_Rendimento_Campos_em_Branco", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
