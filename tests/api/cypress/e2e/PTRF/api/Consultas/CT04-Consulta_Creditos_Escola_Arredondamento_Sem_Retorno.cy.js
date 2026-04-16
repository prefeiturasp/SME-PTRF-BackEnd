///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"

const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"

const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Consulta", () => {
  it("CT04-Consulta_Escola_Arredondamento_Sem_Retorno", () => {
    
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.selecionarArredondamento()

    Creditos.filtrarReceita()

    Creditos.validarRetornoSemResultado()
    
    Comum.selecionarPerfil()

    Comum.logout()
  })
})
