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

  describe.skip('DRE-Acompanhamento de PC: Prestações de conta Apresentada após Acertos [US120637]', () => {
    beforeEach(() => {
      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
    });

    it('Teste 01: Listagem e filtros',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT01();  
      })  

    it('Teste 02: Seção Recebimento pela Diretoria e Informativos da PC',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT02();  
      })  

    it('Teste 03: Seção Devolutiva da Associação',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT03();  
      }) 

    it('Teste 04: Seção Materiais de Referencia',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT04();  
      })  

    it('Teste 05: Seção Conferência de Lançamentos',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT05();  
      }) 

    it('Teste 06: Seção Conferência de Documentos',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT06();  
      })  

    it('Teste 07: Seção Devolução para Acertos',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT07();  
      })  

    it('Teste 08: Seção Comentários',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT08();  
      })  

    it('Teste 09: Legendas e botao "Ir para listagem"',()=>{

      AcompanhamentoPC.validaPCApresentadaAposAcertosCT09();  
      })  


})