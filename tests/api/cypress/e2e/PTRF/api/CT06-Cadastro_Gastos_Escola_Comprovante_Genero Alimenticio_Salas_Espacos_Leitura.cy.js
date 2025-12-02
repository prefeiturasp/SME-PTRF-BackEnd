///<reference types="cypress" />
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

Cypress.on("uncaught:exception", () => {
  return false;
});

describe("Gastos da Escola - Cadastro", () => {

  it("CT06-Cadastro_Gastos_Escola_Comprovante_Genero_Alimenticio_Salas_Espacos_Leitura", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

  });

});
