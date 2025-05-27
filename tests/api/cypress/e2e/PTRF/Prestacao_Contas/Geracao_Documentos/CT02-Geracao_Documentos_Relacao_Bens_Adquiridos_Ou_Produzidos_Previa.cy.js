//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import GeracaoDocumentosPagina from "../../../../support/Paginas/GeracaoDocumentosPagina"
const PCGeracaoDocumentos = new GeracaoDocumentosPagina

Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Prestacao Contas - Geracao Documentos', () => {

    it.skip('CT02-Geracao_Documentos_Relacao_Bens_Adquiridos_Ou_Produzidos_Previa',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMariaClara();

    PCGeracaoDocumentos.selecionarPrestacaoContas();

    PCGeracaoDocumentos.selecionarGeracaoDocumentos();

    PCGeracaoDocumentos.realizarRelacaoBensAdquiridosOuProduzidosPrevia();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})