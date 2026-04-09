///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Cadastro", () => {
  it("CT02-Cadastro_de_Credito", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(10000)

    Creditos.validarCreditosCadastrados()

    Creditos.selecionarCadastrarCredito()

    Comum.logout()
    
  })
})
