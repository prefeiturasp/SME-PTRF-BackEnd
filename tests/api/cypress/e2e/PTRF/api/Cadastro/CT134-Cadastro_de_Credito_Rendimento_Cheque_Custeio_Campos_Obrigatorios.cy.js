///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe("Credito Escola - Cadastro", () => {
  it("CT134-Cadastro_de_Credito_Rendimento_Cheque_Custeio_Campos_Obrigatorios", () => {
    Comum.visitarPaginaPTRF()

  cy.realizar_login('UE')

  Creditos.selecionarCreditosDaEscola()

  cy.wait(3000)

  Creditos.selecionarCadastrarCredito()

  //Ação: tentar salvar sem preencher dados
  Creditos.salvarCadastroCredito()

  Comum.logout()

  })
})
