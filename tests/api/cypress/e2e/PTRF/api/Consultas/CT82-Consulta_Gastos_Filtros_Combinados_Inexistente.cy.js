///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe('Gastos da Escola - Consulta', () => {

  it('CT82-Consulta_Gastos_Filtros_Combinados_Inexistente', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarFiltrarMaisFiltros() 
    
    Gastos.selecionarAplicacaoCusteio()

    Comum.selecionarPerfil()
    Comum.logout()
  })

  it('CT244-Consulta_Gastos_Sair_e_Reacessar_Com_Filtro', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarFiltrarMaisFiltros() 

    Gastos.selecionarAplicacaoCusteio()

    Comum.logout()

    // novo acesso
    Comum.visitarPaginaPTRF()
    
    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()

    Gastos.selecionarFiltrarMaisFiltros() 

    Gastos.selecionarAplicacaoCusteio()

    Comum.logout()
  })
})
