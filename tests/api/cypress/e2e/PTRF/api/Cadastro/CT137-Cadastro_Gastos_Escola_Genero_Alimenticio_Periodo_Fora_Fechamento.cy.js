///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe("Gastos da Escola - Cadastro", () => {

  it("CT137-Cadastro_Gastos_Escola_Genero_Alimenticio_Periodo_Fora_Fechamento", () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()
    
    cy.wait(3000)

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaComprovanteGeneroAlimenticioSalasEspacosLeitura()

    Comum.logout()

  })
})
