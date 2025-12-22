///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();


Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Gastos da Escola - Cadastro', () => {

    it('CT22-Cadastro_Gastos_Escola_Comprovante_Transferencia_Contas_Bb_Custeio_Incompleto_Nao',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();  

    Gastos.selecionarCadastrarDespesa();

    cy.wait(2000);

    Gastos.validarCadastroDespesaComprovanteTransferenciaContasBbCusteioIncompletoNao();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})