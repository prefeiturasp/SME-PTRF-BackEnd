///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe('Credito Escola - Consulta - Filtros', () => {

  /*it.skip('CT115-Consulta_Mais_Filtros_Acao_Material_Pedagogico', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoMaterialPedagogico()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip('CT185-Consulta_Mais_Filtros_Acao_Material_Pedagogico_Com_Data', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoMaterialPedagogico()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip('CT186-Consulta_Mais_Filtros_Acao_Material_Pedagogico_Com_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoMaterialPedagogico()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip('CT187-Consulta_Mais_Filtros_Acao_Material_Pedagogico_Com_Detalhamento', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaAcaoMaterialPedagogico()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  *//*it.skip('CT188-Consulta_Mais_Filtros_Acao_Material_Pedagogico_Com_Multiplos_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaAcaoMaterialPedagogico()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })
*/})
