///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Gastos = new CreditosEscolaPagina()

describe("Credito Escola - Cadastro", () => {
  it("CT104-Cadastro_de_Credito_Rendimento_Cheque_Livre_Aplicacao", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
