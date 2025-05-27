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

  describe.skip('DRE-Acompanhamento de PC: Prestações de conta Devolvidas para Acertos [US120214]', () => {

    it('CT01-Card-Lista-Filtros',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT01();  
    })  

  it('CT02-Secao-RecebimentoPelaDiretoria-InformativosDaPC',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT02();  
    }) 

  it('CT03-Secao-MateriaisDeReferencia',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT03();  
    })  

  it('CT04-Secao-ConferenciaDeLancamentos',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT04();  
    })  

  it('CT05-Secao-ConferenciaDeDocumentos',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT05();  
    }) 
  
  it('CT06-Secao-DevolucaoParaAcertos',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT06();  
    })  

  it('CT07-Secao-Comentarios',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT07();  
    })

  it('CT08-Legendas-BotaoIrParaListagem',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validaPCDevolvidaParaAcertosCT08();  
    })  

})