//<reference types="cypress" />

import usuarios from "../../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

import ComumPaginaPTRF from "../../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import AcompanhamentoPcPagina from "../../../../../support/Paginas/AcompanhamentoPcPagina";
const AcompanhamentoPC = new AcompanhamentoPcPagina();

// Cypress.on("uncaught:exception", (err, runnable) => {
//   // quando retorna falso previne o  Cypress de falhar o teste
//   return false;
// });

// describe.skip("DRE - Acompanhamento de PC [US104300]", () => {
//   it("CT02-Prestacoes_de_Contas_Nao_Recebidas_Status_Receber_Pc", () => {
//     Comum.visitarPaginaPTRF();

//     Comum.login(usuario.Usuario, usuario.Senha);

//     Comum.selecionarDre();

//     AcompanhamentoPC.validarPrestacoesContasNaoRecebidasStatusReceberPc();

//     Comum.selecionarPerfil();

//     Comum.logout();
//   });
// });
