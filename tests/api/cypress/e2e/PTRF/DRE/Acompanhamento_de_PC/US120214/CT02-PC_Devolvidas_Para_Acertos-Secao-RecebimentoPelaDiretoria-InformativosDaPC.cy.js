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

  describe('DRE-Acompanhamento de PC: Prestações de conta devolvidas para acertos [US120214]', () => {

    it.skip('CT02-PC_Devolvidas_Para_Acertos-Secao-RecebimentoPelaDiretoria-e-InformativosDaPC',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();
    
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT02();  
    
  })  

})