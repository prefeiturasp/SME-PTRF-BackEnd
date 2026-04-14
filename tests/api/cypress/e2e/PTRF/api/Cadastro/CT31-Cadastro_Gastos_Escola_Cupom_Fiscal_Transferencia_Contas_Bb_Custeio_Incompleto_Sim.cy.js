///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()


  describe('Gastos da Escola - Cadastro', () => {

    it('CT31-Cadastro_Gastos_Escola_Cupom_Fiscal_Transferencia_Contas_Bb_Custeio_Incompleto_Sim',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaCupomFiscalTransferenciaContasBbCusteioIncompletoSim()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})