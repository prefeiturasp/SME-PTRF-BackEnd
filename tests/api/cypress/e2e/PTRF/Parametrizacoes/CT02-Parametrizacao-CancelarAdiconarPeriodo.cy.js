//<reference types="cypress" />

import usuarios from "../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import ParametrizacoesPagina from "../../../support/Paginas/ParametrizacoesPagina"
const Parametrizacoes = new ParametrizacoesPagina


Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Parametrizacoes', () => {

    it.skip('CT02-Parametrizacao-CancelarAdiconarPeriodo',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Parametrizacoes.selecionarParametrizacoes();

    Parametrizacoes.selecionarPeriodo();

    Parametrizacoes.adcionarPeriodo();

    Parametrizacoes.cancelarAdcionarPeriodo();

    Comum.selecionarPerfil();
       
    Comum.logout();

  })  

})
