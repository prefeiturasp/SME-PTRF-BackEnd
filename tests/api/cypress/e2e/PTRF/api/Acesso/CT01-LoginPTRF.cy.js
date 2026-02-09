///<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";

const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

Cypress.on('uncaught:exception', (err, runnable) => {
  // previne falha do Cypress
  return false;
});

describe('Login', () => {

  it('Tela de Login', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

  });

});
