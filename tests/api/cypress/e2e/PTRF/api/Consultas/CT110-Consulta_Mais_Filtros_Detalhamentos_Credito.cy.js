///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;
import 'cypress-xpath';

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

describe('Credito Escola - Consulta - Filtros', () => {

  it('CT110-Consulta_Mais_Filtros_Detalhamentos_Credito', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT207-Consulta_Mais_Filtros_Detalhamentos_Credito_Com_Data', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT208-Consulta_Mais_Filtros_Detalhamentos_Credito_Com_Acao_PTRF', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaAcaoPtrf();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT209-Consulta_Mais_Filtros_Detalhamentos_Credito_Com_Multiplos_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaAcaoPtrf();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT210-Consulta_Mais_Filtros_Detalhamentos_Credito_Limpar_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT211-Consulta_Mais_Filtros_Detalhamentos_Credito_Cancelar_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
