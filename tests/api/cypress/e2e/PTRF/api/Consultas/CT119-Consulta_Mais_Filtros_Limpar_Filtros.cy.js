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

describe('Credito Escola - Consulta - Filtros', () => {

  it('CT119-Consulta_Mais_Filtros_Limpar_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCheque();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT169-Consulta_Mais_Filtros_Limpar_Sem_Preencher_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();

    // 🔹 Limpar sem filtros preenchidos
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT170-Consulta_Mais_Filtros_Limpar_Apos_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCheque();

    // 🔹 Limpar após selecionar tipo de conta
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT171-Consulta_Mais_Filtros_Limpar_Apos_Datas', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();

    // 🔹 Limpar após preenchimento das datas
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT172-Consulta_Mais_Filtros_Limpar_Apos_Todos_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCheque();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();

    // 🔹 Limpar após todos os filtros preenchidos
    Creditos.selecionarLimparFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
