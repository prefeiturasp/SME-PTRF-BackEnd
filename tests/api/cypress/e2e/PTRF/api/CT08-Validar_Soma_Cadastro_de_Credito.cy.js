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

describe("Credito Escola - Cadastro", () => {
  it("CT08-Validar_Soma_Cadastro_de_Credito", () => {
    Comum.visitarPaginaPTRF();

    // Comum.login(usuario.Usuario, usuario.Senha);

    // Comum.selecionarCeuVilaAlpina();

    // Creditos.selecionarCreditosDaEscola();

    // Creditos.selecionarRendimento();

    // Creditos.filtrarReceita();

    // Creditos.validarCreditosCadastrados();
  });
});
