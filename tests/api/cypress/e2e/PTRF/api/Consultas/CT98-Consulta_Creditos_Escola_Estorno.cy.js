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
  // quando retorna falso previne o Cypress de falhar o teste
  return false;
});

describe("Credito Escola - Consulta", () => {

  it("CT98-Consulta_Creditos_Escola_Estorno", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);

    Creditos.selecionarEstorno();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it("CT220-Consulta_Creditos_Escola_Estorno_Sem_Filtro", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);

    Creditos.selecionarEstorno();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it("CT221-Consulta_Creditos_Escola_Estorno_Reconsultar", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);

    Creditos.selecionarEstorno();
    Creditos.selecionarEstorno();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it("CT222-Consulta_Creditos_Escola_Estorno_Reabrir_Tela", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();
    cy.wait(3000);

    Creditos.selecionarEstorno();

    Comum.logout();

    // Novo acesso
    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarEstorno();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
