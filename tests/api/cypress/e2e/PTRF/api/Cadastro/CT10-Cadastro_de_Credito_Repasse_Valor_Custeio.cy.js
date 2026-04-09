///<reference types="cypress" />
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina();

describe("Credito Escola - Cadastro", () => {
  it("CT10-Cadastro_de_Credito_Repasse_Valor_Custeio", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Creditos.selecionarCreditosDaEscola()

    cy.wait(3000)

    Creditos.validarCreditosCadastrados()

    Creditos.selecionarCadastrarCredito()

    Comum.logout()
  })
})
