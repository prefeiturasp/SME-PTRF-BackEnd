///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {

  /*it.skip("CT95-Consulta_Escola_Arredondamento_Sem_Retorno", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRecursoExterno()

    Creditos.filtrarReceita()

    Comum.logout()
  })

  *//*it.skip("CT227-Consulta_Credito_Escola_Com_Recurso_Externo", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRecursoExterno()

    Creditos.filtrarReceita()

    Comum.logout()
  })

  *//*it.skip("CT228-Consulta_Credito_Escola_Sem_Aplicar_Filtro", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRecursoExterno()

    Comum.logout()
  })

  *//*it.skip("CT229-Consulta_Credito_Escola_Acesso_Tela", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    Comum.logout()
  })

  *//*it.skip("CT230-Consulta_Credito_Escola_Recurso_Externo_Com_Repeticao_Filtro", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarRecursoExterno()

    Creditos.filtrarReceita()

    Creditos.filtrarReceita()
    
    Comum.logout()
  })
*/})
