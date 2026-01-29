///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import CreditosEscolaPagina from "../../../../support/Paginas/CreditosEscolaPagina";
const Creditos = new CreditosEscolaPagina();

Cypress.on("uncaught:exception", (err, runnable) => {
  return false;
});

describe('Credito Escola - Consulta - Mais Filtros - Tipo_Cheque', () => {

  it('CT132-Consulta_Mais_Filtros_Repasse_Cheque', () => {

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarMaisFiltros();

    Creditos.selecionarRepasseMaisFiltros();

    Creditos.selecionarDetalhamentoMaisFiltros();

    Creditos.realizaConsultaTipoContaCheque();

    Creditos.realizaConsultaAcaoPtrf();

    Creditos.realizaConsultaDataInicio();

    Creditos.realizaConsultaDataFim();

    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();

    Comum.logout();
  });

  it('CT139-Consulta_Mais_Filtros_Repasse_Cheque_Sem_Data', () => {

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarMaisFiltros();

    Creditos.selecionarRepasseMaisFiltros();

    Creditos.selecionarDetalhamentoMaisFiltros();

    Creditos.realizaConsultaTipoContaCheque();

    Creditos.realizaConsultaAcaoPtrf();

    // 🔹 Não aplica filtro de data
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();

    Comum.logout();
  });

});
