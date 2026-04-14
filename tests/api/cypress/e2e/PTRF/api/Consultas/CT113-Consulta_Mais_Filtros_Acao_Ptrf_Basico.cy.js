///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe('Credito Escola - Consulta - Filtros', () => {

  it('CT113-Consulta_Mais_Filtros_Acao_Ptrf_Basico', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT193-Consulta_Mais_Filtros_Acao_Ptrf_Basico_Com_Data', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT194-Consulta_Mais_Filtros_Acao_Ptrf_Basico_Com_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT195-Consulta_Mais_Filtros_Acao_Ptrf_Basico_Com_Detalhamento', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT196-Consulta_Mais_Filtros_Acao_Ptrf_Basico_Com_Multiplos_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaAcaoPtrf()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarFiltrarMaisFiltros()

    Comum.selecionarPerfil()

    Comum.logout()
  })
})
