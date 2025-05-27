//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GeracaoDocumentosPagina from "../../../../support/Paginas/GeracaoDocumentosPagina";
const PCGeracaoDocumentos = new GeracaoDocumentosPagina();

// Cypress.on("uncaught:exception", (err, runnable) => {
//   // quando retorna falso previne o  Cypress de falhar o teste
//   return false;
// });

// describe.skip("Prestacao Contas - Geracao Documentos", () => {
//   it("CT04-Geracao_Documentos_Concluir_Periodo", () => {
//     Comum.visitarPaginaPTRF();

//     Comum.login(usuario.Usuario, usuario.Senha);

//     Comum.selecionarCeuEmefMarioFittipaldi();

//     PCGeracaoDocumentos.selecionarPrestacaoContas();

//     PCGeracaoDocumentos.selecionarGeracaoDocumentos();

//     PCGeracaoDocumentos.realizarConcluirPeriodo();

//     // Comum.selecionarPerfil();

//     // Comum.logout();
//   });
// });
