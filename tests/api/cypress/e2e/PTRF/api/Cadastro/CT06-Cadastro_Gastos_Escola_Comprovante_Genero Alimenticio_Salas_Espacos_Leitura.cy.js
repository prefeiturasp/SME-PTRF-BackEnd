///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe("Gastos da Escola - Cadastro", () => {

  it("CT06-Cadastro_Gastos_Escola_Comprovante_Genero_Alimenticio_Salas_Espacos_Leitura", () => {

    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()
    
    cy.wait(3000)

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaComprovanteGeneroAlimenticioPtrf_Basico()

    Comum.logout()

  })
})
