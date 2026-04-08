///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

  describe('Gastos da Escola - Cadastro', () => {

    it('CT50-Cadastro_Gastos_Escola_Incompleto_Boletim_Ocorrencia_Nao_Preenchido',()=>{

    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroGastosEscolaIncompletoBoletimOcorrenciaNaoPreenchido()
    
    Comum.selecionarPerfil()

    Comum.logout()
    
  })  
})