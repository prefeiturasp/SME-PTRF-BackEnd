///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT25-Cadastro_Gastos_Escola_Comprovante_Capital_Material_Pedagogico',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    cy.wait(2000) 

    Gastos.validarCadastroDespesaComprovanteCapitalMaterialPedagogico()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})