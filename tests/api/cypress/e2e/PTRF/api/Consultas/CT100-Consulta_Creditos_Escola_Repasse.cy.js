///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  it("CT100-Consulta_Creditos_Escola_Repasse", () => {

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

  it("CT212-Consulta_Creditos_Escola_Repasse_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRepasse()

    Creditos.validarCreditosCadastrados()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it("CT213-Consulta_Creditos_Escola_Repasse_Com_Filtro_Receita", () => {

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

  it("CT214-Consulta_Creditos_Escola_Repasse_Reconsultar", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRepasse()

    Creditos.filtrarReceita()

    Creditos.validarCreditosCadastrados()

    Creditos.selecionarRepasse()

    Creditos.validarCreditosCadastrados()

    Comum.selecionarPerfil()

    Comum.logout()
  })
})
