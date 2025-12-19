///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;
import 'cypress-xpath';

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../support/Paginas/CreditosEscolaPagina";

const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

  describe('Credito Escola - Consulta - Filtros', () => {

    it('CT110-Consulta_Mais_Filtros_Detalhamentos_Credito',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMariaClara();

    Creditos.selecionarCreditosDaEscola();

    cy.wait(3000);

    Creditos.selecionarMaisFiltros();

    Creditos.selecionarDetalhamentoMaisFiltros();

    Creditos.selecionarFiltrarMaisFiltros();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})