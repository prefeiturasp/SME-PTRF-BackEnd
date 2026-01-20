//<reference types="cypress" />

import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Josue;

import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  // quando retorna falso previne o  Cypress de falhar o teste
  return false;
});

describe("Credito Escola - Consulta", () => {
  it("CT135-Consulta_Escola_Arredondamento_Validar_Credito", () => {
    
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.filtrarReceita();

    Creditos.validar_soma();

    Comum.logout();
  });
});
