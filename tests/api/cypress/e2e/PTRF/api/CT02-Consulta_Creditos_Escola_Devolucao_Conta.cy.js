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
  it("CT02-Consulta_Creditos_Escola_Devolucao_Conta", () => {
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarselecaoEMEF();

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarDevolacaoConta();

    Creditos.filtrarReceita();

    Creditos.validarCreditosCadastrados();

    Comum.selecionarPerfil();

    Comum.logout();
  });
});
