///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe("Gastos da Escola - Cadastro", () => {
  it("CT34-Cadastro_Gastos_Escola_Cupom_Fiscal_Capital_Salas_Espacos_Leitura", () => {
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaCupomFiscalCapitalSalasEspacosLeitura()

    Comum.selecionarPerfil()

    Comum.logout()
    
  })
})
