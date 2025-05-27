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

  describe.skip('DRE-Acompanhamento de PC: Prestações de conta Recebida após acertos [US121917]', () => {
    beforeEach(() => {
      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
    });

    it('Teste 01: Listagem e filtros',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT01();  
      })  

    it('Teste 02: Seção Recebimento pela Diretoria, Devolutiva da Associação e Informativos da PC',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT02();  
      })  

    it('Teste 03: Seção Materiais de Referencia',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT03();  
      })  

    it('Teste 04: Seção Conferência de Lançamentos',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT04();  
      }) 

    it('Teste 05: Seção Conferência de Documentos',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT05();  
      })  

    it('Teste 06: Seção Devolução para Acertos',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT06();  
      })  

    it('Teste 07: Seção Comentários',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT07();  
      })  

    it('Teste 08: Legendas e opções de botões',()=>{

      AcompanhamentoPC.validaPCRecebidaAposAcertosCT08();  
      })  


})