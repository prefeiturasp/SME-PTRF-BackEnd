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

  describe.skip('DRE-Acompanhamento de PC: Prestações de contas Em Análise [US118021 e US118994]', () => {

    it('CT01-Secao-MateriaisDeReferencia',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseParte1MateriaisDeReferencia();  
      })  

    it('CT01-Secao-ConferenciaDeLancamentos-ContaCartao-Filtros',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaCartaoFiltros1();  
      })  

    it('CT02-Secao_ConferenciaDeLancamentos-ContaCartao-MaisFiltros',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaCartaoFiltros2();  
      })  

    it('CT03-Secao-ConferenciaDeLancamentos-ContaCheque-Filtros',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaChequeFiltros3();  
      })  

    it('CT04-Secao-ConferenciaDeLancamentos-ContaCheque-MaisFiltros',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaChequeFiltros4();  
      })  

    it('CT05-Secao-ConferenciaDeLancamentos-ContaCheque-Ordenacao',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaChequeOrdenacao();  
      })  

    it('CT06-Secao-ConferenciaDeLancamentos-ContaCartao-Ordenacao',()=>{

      Comum.visitarPaginaPTRF();
      Comum.login(usuario.Usuario, usuario.Senha);
      Comum.selecionarDre();
      AcompanhamentoPC.validarPCEmAnaliseConferenciaLancamentoContaCartaoOrdenacao();  
      })  

})