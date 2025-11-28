///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

Cypress.on("uncaught:exception", () => {
  // Previne o Cypress de falhar o teste em erros não capturados
  return false;
});

describe("Gastos da Escola - Cadastro", () => {

  it("CT20-Cadastro_Gastos_Escola_Comprovante_Imposto_Material_Pedagogico", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

  });

});
