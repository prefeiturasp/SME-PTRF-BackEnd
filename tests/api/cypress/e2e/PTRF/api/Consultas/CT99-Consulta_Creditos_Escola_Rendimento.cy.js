//<reference types="cypress" />

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

  it("CT99-Consulta_Creditos_Escola_Rendimento", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRendimento();
    Creditos.filtrarReceita();

    Comum.logout();
  });

  it("CT215-Consulta_Creditos_Escola_Rendimento_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRendimento();

    Comum.logout();
  });

  it("CT216-Consulta_Creditos_Escola_Rendimento_Com_Filtro_Receita", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRendimento();
    Creditos.filtrarReceita();

    Comum.logout();
  });

  it("CT217-Consulta_Creditos_Escola_Rendimento_Reconsultar", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarRendimento();
    Creditos.filtrarReceita();

    Creditos.selecionarRendimento();

    Comum.logout();
  });
});
