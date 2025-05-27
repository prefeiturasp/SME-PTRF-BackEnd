//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina


Cypress.on('uncaught:exception', (err, runnable) => {
    return false
  })

  describe('Credito Escola - Consulta', () => {

    it('CT01-Consulta_Creditos_Escola_Arredondamento',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarselecaoEMEF();

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarArredondamento();

    Creditos.filtrarReceita();

    Creditos.validarCreditosCadastrados();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})