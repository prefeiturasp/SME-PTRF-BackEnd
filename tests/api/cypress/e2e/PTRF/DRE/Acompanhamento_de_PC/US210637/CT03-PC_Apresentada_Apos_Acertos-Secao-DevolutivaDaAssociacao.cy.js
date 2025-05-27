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

  describe('DRE-Acompanhamento de PC: Prestações de conta Apresentadas após acertos [US120637]', () => {

    it.skip('CT03-PC_Apresentada_Apos_Acertos-Secao-DevolutivaDaAssociacao',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();
    
    AcompanhamentoPC.validaPCApresentadaAposAcertosCT03();  
    
  })  

})