///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Consulta', () => {

    it('CT59-Consulta_Gastos_Escola_Acao_Ptrf',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarFiltrarMaisFiltros() 
    
    Gastos.selecionarAplicacaoCusteio()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})