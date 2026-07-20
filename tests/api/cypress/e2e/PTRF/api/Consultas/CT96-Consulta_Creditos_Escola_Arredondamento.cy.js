///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  /*it.skip("CT96-Consulta_Creditos_Escola_Arredondamento", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')  

    Creditos.selecionarCreditosDaEscola()
  })

  *//*it.skip("CT225-Consulta_Creditos_Escola_Arredondamento_Sem_Filtros", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarArredondamento?.()

    Comum.logout()
  })

  *//*it.skip("CT226-Consulta_Creditos_Escola_Arredondamento_Reconsultar", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarArredondamento?.()
    
    Creditos.selecionarArredondamento?.()

    Comum.logout()
  })
*/})
