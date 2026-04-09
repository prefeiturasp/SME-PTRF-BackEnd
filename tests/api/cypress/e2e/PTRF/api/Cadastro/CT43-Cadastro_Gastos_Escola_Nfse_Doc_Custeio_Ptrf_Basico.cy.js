///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT43-Cadastro_Gastos_Escola_Nfse_Doc_Custeio_Ptrf_Basico',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroGastosEscolaNfseDocCusteioPtrfBasico()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})