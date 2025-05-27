//<reference types="cypress" />

import usuarios from "../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina


Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Gastos da Escola - Cadastro', () => {

    it('CT35-Cadastro_Gastos_Escola_Incompleto_Danfe_Cheque_Continuar_Preenchendo_Campos_Sim',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();  

    Gastos.selecionarCadastrarDespesa();

    Gastos.validarCadastroGastosEscolaIncompletoDanfeChequeContinuarPreenchendoCamposSim();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})