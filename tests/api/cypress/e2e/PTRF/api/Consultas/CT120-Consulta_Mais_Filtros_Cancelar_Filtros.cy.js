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

  it('CT120-Consulta_Mais_Filtros_Cancelar_Filtros', () => {

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
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT165-Consulta_Mais_Filtros_Cancelar_Sem_Preencher_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();

    // 🔹 Cancelar sem aplicar filtros
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT166-Consulta_Mais_Filtros_Cancelar_Apos_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.realizaConsultaTipoContaCheque();

    // 🔹 Cancelar após selecionar tipo de conta
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT167-Consulta_Mais_Filtros_Cancelar_Apos_Datas', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarArredondamentoMaisFiltros();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();

    // 🔹 Cancelar após preenchimento de datas
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT168-Consulta_Mais_Filtros_Cancelar_Apos_Todos_Filtros', () => {

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

    // 🔹 Cancelar após todos os filtros preenchidos
    Creditos.selecionarCancelar();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
