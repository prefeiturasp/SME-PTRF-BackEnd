///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"

const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {
  it("CT15-Consulta_Creditos_Escola_Recurso_Externo", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRecursoExterno()

    Creditos.filtrarReceita()

    Comum.logout()
  })
})
