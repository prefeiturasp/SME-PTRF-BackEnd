//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina


Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Credito Escola - Consulta', () => {

    it('CT07-Consulta_Escola_Arredondamento_Sem_Retorno',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarArredondamento();

    Creditos.filtrarReceita();

    Creditos.validarRetornoSemResultado();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})