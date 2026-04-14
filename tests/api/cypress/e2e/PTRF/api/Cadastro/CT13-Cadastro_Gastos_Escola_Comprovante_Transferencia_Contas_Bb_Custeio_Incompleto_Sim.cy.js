///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

  describe('Gastos da Escola - Cadastro', () => {

    it('CT13-Cadastro_Gastos_Escola_Comprovante_Transferencia_Contas_Bb_Custeio_Incompleto_Sim',()=>{

    Comum.visitarPaginaPTRF();

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola();
    
    cy.wait(2000);

    Gastos.selecionarCadastrarDespesa();

    Gastos.validarCadastroDespesaComprovanteTransferenciaContasBbCusteioIncompletoSim();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})