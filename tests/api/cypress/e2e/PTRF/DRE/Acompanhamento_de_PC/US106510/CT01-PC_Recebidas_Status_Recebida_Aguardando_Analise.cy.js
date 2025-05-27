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

  describe('DRE - Acompanhamento de PC [US106510]', () => {

    it.skip('CT01-PC_Recebidas_Status_Recebida_Aguardando_Analise',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();
    
    AcompanhamentoPC.validarPCRecebidasStatusAguardandoAnalise();  
    
  })  

})