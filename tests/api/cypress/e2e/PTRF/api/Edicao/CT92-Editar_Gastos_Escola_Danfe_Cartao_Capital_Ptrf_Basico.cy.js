///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Editar', () => {

    it('CT92-Editar_Gastos_Escola_Danfe_Cartao_Capital_Ptrf_Basico',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarFiltrarMaisFiltros() 
    
    Gastos.selecionarAplicacaoCusteio()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})