//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

// Cypress.on("uncaught:exception", (err, runnable) => {
//   // quando retorna falso previne o  Cypress de falhar o teste
//   return false;
// });

// describe.skip("Gastos da Escola - Consulta", () => {
//   it("CT15-Consulta_Gastos_Escola_Informacao_Imposto", () => {
//     Comum.visitarPaginaPTRF();

//     Comum.login(usuario.Usuario, usuario.Senha);

//     Comum.selecionarCeuVilaAlpina();

//     Gastos.selecionarGastosDaEscola();

//     Gastos.selecionarFiltrarMaisFiltros();

//     Gastos.selecionarInformacaoImposto();

//     Comum.selecionarPerfil();

//     Comum.logout();
//   });
// });
