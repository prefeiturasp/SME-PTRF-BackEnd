///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../support/Paginas/CreditosEscolaPagina";

const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});


  describe('Credito Escola - Consulta - Mais Filtros - Tipo_Cartao', () => {

    it('CT125-Consulta_Mais_Filtros_Rendimento_Cheque',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarMaisFiltros();

    Creditos.selecionarRendimentoMaisFiltros();

    Creditos.selecionarDetalhamentoMaisFiltros();

    Creditos.realizaConsultaTipoContaCartao();

    Creditos.realizaConsultaAcaoPtrf();

    Creditos.realizaConsultaDataInicio();

    Creditos.realizaConsultaDataFim();

    Creditos.selecionarFiltrarMaisFiltros();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})