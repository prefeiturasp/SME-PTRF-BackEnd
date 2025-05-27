//<reference types="cypress" />

import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import ResumoPagina from "../../../support/Paginas/ResumoPagina";
const Resumo = new ResumoPagina();

// Cypress.on("uncaught:exception", (err, runnable) => {
//   // quando retorna falso previne o  Cypress de falhar o teste
//   return false;
// });

// describe.skip("Parametrizacoes", () => {
//   it("CT09-Resumo_dos_Recursos-TipoCheque", () => {
//     Comum.visitarPaginaPTRF();

//     Comum.login(usuario.Usuario, usuario.Senha);

//     Comum.selecionarselecaoEMEF();

//     Resumo.selecionarResumo();

//     Resumo.selecionarPeriodo();

//     // Resumo.selecionarTipoCheque();

//     Comum.selecionarPerfil();

//     Comum.logout();
//   });
// });
