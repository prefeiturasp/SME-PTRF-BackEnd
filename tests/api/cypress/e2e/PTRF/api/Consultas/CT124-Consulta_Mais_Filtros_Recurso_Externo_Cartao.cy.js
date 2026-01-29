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

  it('CT124-Consulta_Mais_Filtros_Recurso_Externo_Cartao', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarRecursoExternoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.realizaConsultaAcaoPtrf();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT151-Consulta_Mais_Filtros_Recurso_Externo_Cartao_Sem_Data', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarRecursoExternoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.realizaConsultaAcaoPtrf();

    // 🔹 Sem data início e fim
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT152-Consulta_Mais_Filtros_Recurso_Externo_Cartao_Sem_Acao', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarRecursoExternoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCartao();

    // 🔹 Sem ação PTRF
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT153-Consulta_Mais_Filtros_Recurso_Externo_Cartao_Somente_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarRecursoExternoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();

    // 🔹 Apenas tipo de conta Cartão
    Creditos.realizaConsultaTipoContaCartao();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
