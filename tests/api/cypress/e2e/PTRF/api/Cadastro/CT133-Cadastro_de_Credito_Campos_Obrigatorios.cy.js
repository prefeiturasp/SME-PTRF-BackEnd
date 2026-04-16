///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"

const Creditos = new CreditosEscolaPagina()

it("CT133-Cadastro_de_Credito_Campos_Obrigatorios", () => {
  Comum.visitarPaginaPTRF()

  cy.realizar_login('UE')

  Creditos.selecionarCreditosDaEscola()

  cy.wait(10000)

  Creditos.selecionarCadastrarCredito()

  Creditos.salvarCadastroCredito()

  Comum.logout()  
})
