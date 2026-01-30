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

describe('Credito Escola - Consulta - Filtros', () => {

  it('CT117-Consulta_Mais_Filtros_Acao_Material_Complementar', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.realizaConsultaAcaoMaterialComplementar();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT177-Consulta_Mais_Filtros_Acao_Material_Complementar_Com_Data', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.realizaConsultaAcaoMaterialComplementar();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT178-Consulta_Mais_Filtros_Acao_Material_Complementar_Com_Tipo_Conta', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.realizaConsultaAcaoMaterialComplementar();
    Creditos.realizaConsultaTipoContaCheque();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT179-Consulta_Mais_Filtros_Acao_Material_Complementar_Com_Detalhamento', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaAcaoMaterialComplementar();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT180-Consulta_Mais_Filtros_Acao_Material_Complementar_Com_Multiplos_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);
    Comum.selecionarCeuEmefMariaClara();

    cy.wait(3000);

    Creditos.selecionarCreditosDaEscola();
    Creditos.selecionarMaisFiltros();
    Creditos.selecionarDetalhamentoMaisFiltros();
    Creditos.realizaConsultaAcaoMaterialComplementar();
    Creditos.realizaConsultaTipoContaCheque();
    Creditos.realizaConsultaDataInicio();
    Creditos.realizaConsultaDataFim();
    Creditos.selecionarFiltrarMaisFiltros();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
