///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"

const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"

const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  /*it.skip("CT05-Consulta_Creditos_Escola_Devolucao_Conta", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarDevolacaoConta()
    Creditos.filtrarReceita()

    Comum.logout()
  })

  *//*it.skip("CT226-Consulta_Creditos_Escola_Devolucao_Conta_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarDevolacaoConta()

    Comum.logout()
  })

  *//*it.skip("CT227-Consulta_Creditos_Escola_Devolucao_Conta_Reconsultar", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()
    
    cy.wait(3000)

    Creditos.selecionarDevolacaoConta()
    Creditos.filtrarReceita()

    // Reconsulta
    Creditos.selecionarDevolacaoConta()
    Creditos.filtrarReceita()

    Comum.logout()
  })
*/})
