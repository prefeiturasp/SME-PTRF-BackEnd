//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Josue;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  // quando retorna falso previne o  Cypress de falhar o teste
  return false;
});

describe("Credito Escola - Consulta", () => {
  it("CT04-Consulta_Creditos_Escola_Recurso_Externo", () => {
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMarioFittipaldi();

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarRecursoExterno();

    Creditos.filtrarReceita();

    Creditos.validarCreditosCadastrados();

    Comum.selecionarPerfil();

    Comum.logout();
  });
});
