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

  it("CT95-Consulta_Escola_Arredondamento_Sem_Retorno", () => {
    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);
    Creditos.selecionarRecursoExterno();
    Creditos.filtrarReceita();
    Comum.logout();
  });

  it("CT227-Consulta_Credito_Escola_Com_Recurso_Externo", () => {
    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);
    Creditos.selecionarRecursoExterno();
    Creditos.filtrarReceita();
    Comum.logout();
  });

  it("CT228-Consulta_Credito_Escola_Sem_Aplicar_Filtro", () => {
    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);
    Creditos.selecionarRecursoExterno();
    Comum.logout();
  });

  it("CT229-Consulta_Credito_Escola_Acesso_Tela", () => {
    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();
    Creditos.selecionarCreditosDaEscola();
    Comum.logout();
  });

  it("CT230-Consulta_Credito_Escola_Recurso_Externo_Com_Repeticao_Filtro", () => {
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
});
