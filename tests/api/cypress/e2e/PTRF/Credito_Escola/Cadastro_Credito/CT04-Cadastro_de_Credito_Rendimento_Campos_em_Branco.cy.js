//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  // quando retorna falso previne o  Cypress de falhar o teste
  return false;
});

describe.skip("Credito Escola - Cadastro", () => {
  it("CT04-Cadastro_de_Credito_Rendimento_Campos_em_Branco", () => {
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    Creditos.validarCreditosCadastrados();

    Creditos.selecionarCadastrarCredito();

    Creditos.realizarCadastroCreditoRendimentoCamposEmBranco();

    Comum.selecionarPerfil();

    Comum.logout();
  });
});
