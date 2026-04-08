///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT24-Cadastro_Gastos_Escola_Comprovante_Capital_Salas_Espacos_Leitura',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    cy.wait(2000)

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaComprovanteCapitalSalasEspacosLeitura()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})