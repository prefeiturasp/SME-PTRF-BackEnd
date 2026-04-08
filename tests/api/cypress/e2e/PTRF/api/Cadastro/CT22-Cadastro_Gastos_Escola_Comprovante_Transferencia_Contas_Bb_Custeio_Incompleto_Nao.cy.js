///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT22-Cadastro_Gastos_Escola_Comprovante_Transferencia_Contas_Bb_Custeio_Incompleto_Nao',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    cy.wait(2000)

    Gastos.validarCadastroDespesaComprovanteTransferenciaContasBbCusteioIncompletoNao()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})