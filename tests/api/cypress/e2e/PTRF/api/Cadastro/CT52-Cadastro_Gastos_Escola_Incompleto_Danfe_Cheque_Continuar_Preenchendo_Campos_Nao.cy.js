///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()


  describe('Gastos da Escola - Cadastro', () => {

    it('CT52-Cadastro_Gastos_Escola_Incompleto_Danfe_Cheque_Continuar_Preenchendo_Campos_Sim',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroGastosEscolaIncompletoDanfeChequeContinuarPreenchendoCamposNao()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})