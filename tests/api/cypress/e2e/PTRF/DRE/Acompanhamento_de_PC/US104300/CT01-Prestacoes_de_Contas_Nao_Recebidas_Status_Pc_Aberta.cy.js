//<reference types="cypress" />

import usuarios from "../../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import AcompanhamentoPcPagina from "../../../../../support/Paginas/AcompanhamentoPcPagina"
const AcompanhamentoPC = new AcompanhamentoPcPagina

Cypress.on('uncaught:exception', (err, runnable) => {

    return false
  })

  describe('DRE - Acompanhamento de PC [US104300]', () => {

    it.skip('CT01-Prestacoes_de_Contas_Nao_Recebidas_Status_Pc_Aberta',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();

    AcompanhamentoPC.validarPrestacoesContasNaoRecebidasPcAbertas();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})