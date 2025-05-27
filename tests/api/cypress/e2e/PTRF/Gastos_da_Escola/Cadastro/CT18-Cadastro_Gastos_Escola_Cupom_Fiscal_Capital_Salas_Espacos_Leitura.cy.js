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

// describe.skip("Gastos da Escola - Cadastro", () => {
//   it("CT18-Cadastro_Gastos_Escola_Cupom_Fiscal_Capital_Salas_Espacos_Leitura", () => {
//     Comum.visitarPaginaPTRF();

//     Comum.login(usuario.Usuario, usuario.Senha);

//     Comum.selecionarCeuVilaAlpina();

//     Gastos.selecionarGastosDaEscola();

//     Gastos.selecionarCadastrarDespesa();

//     Gastos.validarCadastroDespesaCupomFiscalCapitalSalasEspacosLeitura();

//     Comum.selecionarPerfil();

//     Comum.logout();
//   });
// });
