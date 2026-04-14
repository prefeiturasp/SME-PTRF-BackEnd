///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  it("CT97-Consulta_Creditos_Escola_Devolucao_Conta", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Gastos.selecionarDevolucaoConta?.()

    Comum.logout()
  })

  it("CT223-Consulta_Creditos_Escola_Devolucao_Conta_Sem_Filtros", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Gastos.selecionarDevolucaoConta?.()

    Comum.logout()
  })

  it("CT224-Consulta_Creditos_Escola_Devolucao_Conta_Reconsultar", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Gastos.selecionarDevolucaoConta?.()
    Gastos.selecionarDevolucaoConta?.()

    Comum.logout()
  })
})
