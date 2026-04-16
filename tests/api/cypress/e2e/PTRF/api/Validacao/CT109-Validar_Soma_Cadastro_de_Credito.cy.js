///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Gastos = new CreditosEscolaPagina()

describe("Credito Escola - Cadastro", () => {
  it("CT109-Validar_Soma_Cadastro_de_Credito", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')
  })
})
