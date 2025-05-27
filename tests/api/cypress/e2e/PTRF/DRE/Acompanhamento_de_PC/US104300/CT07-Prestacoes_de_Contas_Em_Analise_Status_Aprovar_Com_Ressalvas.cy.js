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

  describe('DRE - Acompanhamento de PC [US104300]', () => {

    it.skip('CT07-Prestacoes_de_Contas_Em_Analise_Status_Aprovar_Com_Ressalvas',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarDre();

    AcompanhamentoPC.validarPrestacoesContasEmAnaliseStatusAprovarComRessalvas();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})