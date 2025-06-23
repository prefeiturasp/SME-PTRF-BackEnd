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
  it("CT02-Cadastro_de_Credito_Rendimento_Cheque_Custeio", () => {
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    Creditos.validarCreditosCadastrados();

    Creditos.selecionarCadastrarCredito();

    Creditos.realizarCadastroCreditoRendimentoCusteioCheque();

    Comum.selecionarPerfil();

    Comum.logout();
  });
});
