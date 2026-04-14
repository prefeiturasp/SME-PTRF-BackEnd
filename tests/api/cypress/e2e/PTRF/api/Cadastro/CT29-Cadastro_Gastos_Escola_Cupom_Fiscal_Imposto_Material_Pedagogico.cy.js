///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT29-Cadastro_Gastos_Escola_Cupom_Fiscal_Imposto_Material_Pedagogico',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaCupomFiscalImpostoMaterialPedagogico()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})