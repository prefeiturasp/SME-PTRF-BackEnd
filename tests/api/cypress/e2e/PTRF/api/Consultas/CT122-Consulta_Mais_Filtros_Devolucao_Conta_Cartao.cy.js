///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

describe('Credito Escola - Consulta - Mais Filtros - Tipo_Cartao', () => {

  it('CT122-Consulta_Mais_Filtros_Devolucao_Conta_Cartao', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDevolacaoContaMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.realizaConsultaAcaoPtrf();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT157-Consulta_Mais_Filtros_Devolucao_Conta_Cartao_Sem_Data', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDevolacaoContaMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.realizaConsultaAcaoPtrf();

    // 🔹 Sem data início e fim
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT158-Consulta_Mais_Filtros_Devolucao_Conta_Cartao_Sem_Acao', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDevolacaoContaMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();

    // 🔹 Sem ação PTRF
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT159-Consulta_Mais_Filtros_Devolucao_Conta_Cartao_Somente_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDevolacaoContaMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();

    // 🔹 Apenas tipo de conta Cartão
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT160-Consulta_Mais_Filtros_Devolucao_Conta_Cartao_Sem_Filtros_Complementares', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDevolacaoContaMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();

    // 🔹 Sem tipo de conta, ação e datas
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
