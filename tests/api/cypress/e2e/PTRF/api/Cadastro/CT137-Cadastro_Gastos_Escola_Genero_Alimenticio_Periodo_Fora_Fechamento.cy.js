///<reference types="cypress" />
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

Cypress.on("uncaught:exception", () => {
  return false;
});

describe("Gastos da Escola - Cadastro", () => {

  it("CT137-Cadastro_Gastos_Escola_Genero_Alimenticio_Periodo_Fora_Fechamento", () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    
    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();
    
    cy.wait(3000);

    Gastos.selecionarCadastrarDespesa();

    Gastos.validarCadastroDespesaComprovanteGeneroAlimenticioSalasEspacosLeitura();

    Comum.logout();

  });

});
