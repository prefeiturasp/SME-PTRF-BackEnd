///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina()

describe('Credito Escola - Consulta - Filtros', () => {

  it('CT120-Consulta_Mais_Filtros_Cancelar_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarArredondamentoMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT165-Consulta_Mais_Filtros_Cancelar_Sem_Preencher_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    // Cancelar sem aplicar filtros
    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT166-Consulta_Mais_Filtros_Cancelar_Apos_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarArredondamentoMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    // Cancelar após selecionar tipo de conta
    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT167-Consulta_Mais_Filtros_Cancelar_Apos_Datas', () => {

    Comum.visitarPaginaPTRF()

   cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarArredondamentoMaisFiltros()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    // Cancelar após preenchimento de datas
    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })

  it('CT168-Consulta_Mais_Filtros_Cancelar_Apos_Todos_Filtros', () => {

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    cy.wait(3000)

    Creditos.selecionarCreditosDaEscola()

    Creditos.selecionarMaisFiltros()

    Creditos.selecionarArredondamentoMaisFiltros()

    Creditos.selecionarDetalhamentoMaisFiltros()

    Creditos.realizaConsultaTipoContaCheque()

    Creditos.realizaConsultaDataInicio()

    Creditos.realizaConsultaDataFim()

    // Cancelar após todos os filtros preenchidos
    Creditos.selecionarCancelar()

    Comum.selecionarPerfil()

    Comum.logout()
  })
})
