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

  describe.skip('DRE-Acompanhamento de PC: PC Recebidas [US106510]', () => {

    it('CT01-Alterar-status-para-RecebidaAguardandoAnalise',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPCRecebidasStatusAguardandoAnalise();  
    })  

  it('CT02-Filtros-BotoesdeAcao',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPCRecebidasFiltrosBotoesAcao();  
    })  

  it('CT03-Card-Quantitativo-SemAlteracao',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPCRecebidasQuantitativoCardsInalterado();  
    })  

  it('CT04-Card-Quantitativo-Alterado',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPCRecebidasQuantitativoCardsAlterado();  
    })  

})