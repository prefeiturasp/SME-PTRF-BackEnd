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

  describe.skip('DRE-Acompanhamento de PC: Alteração de Status da PC [US104300]', () => {

  it('CT01-PC-NaoRecebidas-para-status-Aberta',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasNaoRecebidasPcAbertas();
    })  
  
  it('CT02-PC-NaoRecebidas-para-status-Recebida',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasNaoRecebidasStatusReceberPc();
    })  

  it('CT03-PC-Recebidas-voltar-status-NaoRecebidas',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasRecebidasStatusNaoRecebida();
    })  

  it('CT04-PC-Recebidas-para-status-EmAnalise',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasRecebidasStatusPcAnalisar();   
    })  

  it('CT05-PC-EmAnalise-para-status-Recebida',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasEmAnaliseStatusRecebida();   
    })  

  it('CT06-PC-EmAnalise-para-status-Aprovadas',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasEmAnaliseStatusAprovar();
    })  

  it('CT07-PC-EmAnalise-para-status-AprovadaComRessalvas',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasEmAnaliseStatusAprovarComRessalvas();
    })  

  it('CT08-PC-EmAnalise-para-status-Reprovada',()=>{

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarDre();
    AcompanhamentoPC.validarPrestacoesContasEmAnaliseStatusReprovar();
  }) 


})