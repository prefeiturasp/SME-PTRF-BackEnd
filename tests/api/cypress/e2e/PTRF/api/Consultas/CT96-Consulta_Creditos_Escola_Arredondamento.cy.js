///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";

const Creditos = new CreditosEscolaPagina

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

describe("Credito Escola - Consulta", () => {
  it("CT96-Consulta_Creditos_Escola_Arredondamento", () => {
    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();
  });
});
