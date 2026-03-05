//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF";
const Comum = new ComumElementosPTRF();

var esperar = 2000;

class ComumPaginaPTRF {
  visitarPaginaPTRF() {
    cy.visit(Cypress.config("baseUrlPTRF"));
  }

  login(Usuario, Senha) {
    Comum.textoUsuario().type(Usuario);
    Comum.textoSenha().type(Senha);
    Comum.botaoAcessar().click();

    cy.wait(10000);

    const condicaoSelector = ':nth-child(2) > .ant-spin-nested-loading > .ant-spin-container > .ant-card > .ant-card-body > .ant-typography';
    const cliqueSelector   = ':nth-child(2) > .ant-spin-nested-loading > .ant-spin-container > .ant-card > .ant-card-body > div';

    cy.get('body').then($body => {
      if ($body.find(condicaoSelector).length > 0) {
        cy.get(cliqueSelector).click({ force: true });
      }
    });
  }

  selecionarFiltroPrincipal() {
    Comum.botaoFiltroPrincipal().click({ force: true });
  }

  selecionarselecaoEMEF() {
    Comum.selecaoEMEF().should("be.visible");
  }

  selecionarCeuEmefMariaClara() {
    cy.wait(esperar);
    Comum.selecaoCeuEmefMariaClara().should("be.visible");
  }

  selecionarCeuEmefMarioFittipaldi() {
    cy.wait(esperar);
    Comum.selecaoCeuEmefMarioFittipaldi().should("be.visible");
  }

  selecionarCeuVilaAlpina() {
    cy.wait(esperar);
    Comum.selecaoCeuVilaAlpina().should("be.visible");
  }

  selecionarDre() {
    cy.wait(esperar);
    Comum.selecaoDRE().should("be.visible");
    cy.wait(esperar);
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
    cy.wait(esperar);
    Comum.botaoSair().click({ force: true });
    // Comum.botaoSairSistema().click();
  }
}

export default ComumPaginaPTRF;
