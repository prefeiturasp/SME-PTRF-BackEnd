///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  /*it.skip("CT98-Consulta_Creditos_Escola_Estorno", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarEstorno()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip("CT220-Consulta_Creditos_Escola_Estorno_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarEstorno()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip("CT221-Consulta_Creditos_Escola_Estorno_Reconsultar", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()
    cy.wait(3000)

    Creditos.selecionarEstorno()
    Creditos.selecionarEstorno()

    Comum.selecionarPerfil()
    Comum.logout()
  })

  *//*it.skip("CT222-Consulta_Creditos_Escola_Estorno_Reabrir_Tela", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()
    cy.wait(3000)

    Creditos.selecionarEstorno()

    Comum.logout()

    // Novo acesso
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarEstorno()

    Comum.selecionarPerfil()
    Comum.logout()
  })
*/})
