//<reference types="cypress" />

import usuarios from "../../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import AcompanhamentoPcPagina from "../../../../../support/Paginas/AcompanhamentoPcPagina"
const AcompanhamentoPC = new AcompanhamentoPcPagina

Cypress.on('uncaught:exception', (err, runnable) => {
  // quando retorna falso previne o  Cypress de falhar o teste
  return false
})

describe('DRE - Acompanhamento de PC [US104300]', () => {

  it.skip('CT04-Prestacoes_de_Contas_Recebidas_Status_Pc_Analisar', () => {

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();
   
    AcompanhamentoPC.validarPrestacoesContasRecebidasStatusPcAnalisar();

    Comum.selecionarPerfil();

    Comum.logout();

  })

})