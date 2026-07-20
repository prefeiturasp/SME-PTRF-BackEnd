///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  /*it.skip("CT99-Consulta_Creditos_Escola_Rendimento", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRendimento()

    Creditos.filtrarReceita()

    Comum.logout()
  })

  *//*it.skip("CT215-Consulta_Creditos_Escola_Rendimento_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRendimento()

    Comum.logout()
  })

  *//*it.skip("CT216-Consulta_Creditos_Escola_Rendimento_Com_Filtro_Receita", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRendimento()

    Creditos.filtrarReceita()

    Comum.logout()
  })

  *//*it.skip("CT217-Consulta_Creditos_Escola_Rendimento_Reconsultar", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRendimento()
    
    Creditos.filtrarReceita()

    Creditos.selecionarRendimento()

    Comum.logout()
  })
*/})
