//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF";
const Comum = new ComumElementosPTRF();

class ComumPaginaPTRF {
  visitarPaginaPTRF() {
    cy.visit(Cypress.config("baseUrlPTRF"));
  }

  login(Usuario, Senha) {
    Comum.textoUsuario().type(Usuario);
    Comum.textoSenha().type(Senha);
    Comum.botaoAcessar().click();

    cy.wait(3000);
  }

  selecionarFiltroPrincipal() {
    Comum.botaoFiltroPrincipal().click({ force: true });
  }

  selecionarselecaoEMEF() {
    Comum.selecaoEMEF().should("be.visible");
  }

  selecionarCeuEmefMariaClara() {
    cy.wait(3000);
    Comum.selecaoCeuEmefMariaClara().should("be.visible");
  }

  selecionarCeuEmefMarioFittipaldi() {
    cy.wait(3000);
    Comum.selecaoCeuEmefMarioFittipaldi().should("be.visible");
  }

  selecionarCeuVilaAlpina() {
    cy.wait(3000);
    Comum.selecaoCeuVilaAlpina().should("be.visible");
  }

  selecionarDre() {
    cy.wait(3000);
    Comum.selecaoDRE().should("be.visible");
    cy.wait(3000);
  }

  selecionarItemMenuNavegacao() {
    Comum.menuItem().click();
  }

  selecionarPerfil() {
    Comum.botaoPerfil().click();
  }

  selecionarMeusDados() {
    Comum.botaoMeusDados().click();
  }

  logout() {
    cy.wait(3000);
    Comum.botaoSair().click({ force: true });
    // Comum.botaoSairSistema().click();
  }
}

export default ComumPaginaPTRF;
