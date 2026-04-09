///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"

const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"

const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {
  it("CT09-Consulta_Creditos_Escola_Repasse", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRepasse()

    Creditos.filtrarReceita()

    Creditos.validarCreditosCadastrados()
    
    Comum.selecionarPerfil()

    Comum.logout()

  })
})
