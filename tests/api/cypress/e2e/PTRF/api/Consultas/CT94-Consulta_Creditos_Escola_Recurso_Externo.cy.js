///<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Josue;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  // quando retorna falso previne o Cypress de falhar o teste
  return false;
});

describe("Credito Escola - Consulta", () => {

  it("CT94-Consulta_Creditos_Escola_Recurso_Externo", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRecursoExterno();
    Creditos.filtrarReceita();

    Comum.logout();
  });

  it("CT231-Consulta_Creditos_Escola_Acesso_Tela", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();

    Comum.logout();
  });

  it("CT232-Consulta_Creditos_Escola_Recurso_Externo_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRecursoExterno();

    Comum.logout();
  });

  it("CT233-Consulta_Creditos_Escola_Reaplicar_Filtro_Receita", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRecursoExterno();
    Creditos.filtrarReceita();
    Creditos.filtrarReceita();

    Comum.logout();
  });

  it("CT234-Consulta_Creditos_Escola_Navegacao_Completa", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRecursoExterno();
    Creditos.filtrarReceita();

    Comum.logout();
  });

});
