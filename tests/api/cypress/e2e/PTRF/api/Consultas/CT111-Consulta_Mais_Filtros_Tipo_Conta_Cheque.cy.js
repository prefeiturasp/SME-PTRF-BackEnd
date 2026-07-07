///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()


describe('Credito Escola - Consulta - Filtros', () => {

  it.skip('CT111-Consulta_Mais_Filtros_Tipo_Conta_Cheque', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT201-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Com_Data', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT202-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Com_Acao_PTRF', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    cy.wait(5000)

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT203-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Com_Detalhamento', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    cy.wait(5000)

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT204-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Com_Multiplos_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    cy.wait(5000)

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT205-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Limpar_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    cy.wait(5000)

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarLimparFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it.skip('CT206-Consulta_Mais_Filtros_Tipo_Conta_Cheque_Cancelar_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    cy.wait(5000)

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })
})
