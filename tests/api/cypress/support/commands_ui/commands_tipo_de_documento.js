import Tipo_De_Documento_Localizadores from "../locators/tipo_de_documento_locators";
import Commons_Locators from "../locators/commons_locators";

const commons_locators = new Commons_Locators();
const tipo_de_documento_locators = new Tipo_De_Documento_Localizadores();

Cypress.Commands.add(
  "informar_dados_tipo_de_documento",
  (
    nome_tipo_do_documento,
    solicitar_a_digitacao_do_numero_do_documento,
    no_numero_do_documento_deve_constar_apenas_digitos,
    documento_comprobatorio_de_despesa,
    habilita_preenchimento_do_imposto,
    documento_relativo_ao_imposto_recolhido
  ) => {
    cy.get(tipo_de_documento_locators.txt_nome_tipo_de_documento()).clear();
    nome_tipo_do_documento
      ? cy
          .get(tipo_de_documento_locators.txt_nome_tipo_de_documento())
          .type(nome_tipo_do_documento)
      : "";
    if (solicitar_a_digitacao_do_numero_do_documento == "true") {
      cy.get(
        tipo_de_documento_locators.rdb_solicitar_a_digitacao_do_numero_do_documento_sim()
      ).click();
      if (no_numero_do_documento_deve_constar_apenas_digitos == "true") {
        cy.get(
          tipo_de_documento_locators.rdb_no_numero_do_documento_deve_constar_apenas_digitos_sim()
        ).click();
      } else {
        cy.get(
          tipo_de_documento_locators.rdb_no_numero_do_documento_deve_constar_apenas_digitos_nao()
        ).click();
      }
    } else {
      cy.get(
        tipo_de_documento_locators.rdb_solicitar_a_digitacao_do_numero_do_documento_nao()
      ).click();
    }

    if (documento_comprobatorio_de_despesa == "true") {
      cy.get(
        tipo_de_documento_locators.rdb_documento_comprobatorio_de_despesa_sim()
      ).click();
      if (habilita_preenchimento_do_imposto == "true") {
        cy.get(
          tipo_de_documento_locators.rdb_habilita_preenchimento_do_imposto_sim()
        ).click();
      } else {
        cy.get(
          tipo_de_documento_locators.rdb_habilita_preenchimento_do_imposto_nao()
        ).click();
      }
    } else {
      cy.get(
        tipo_de_documento_locators.rdb_documento_comprobatorio_de_despesa_nao()
      ).click();
    }

    if (documento_relativo_ao_imposto_recolhido == "true") {
      cy.get(
        tipo_de_documento_locators.rdb_documento_relativo_ao_imposto_recolhido_sim()
      ).click();
    } else {
      cy.get(
        tipo_de_documento_locators.rdb_documento_relativo_ao_imposto_recolhido_nao()
      ).click();
    }
  }
);

Cypress.Commands.add(
  "clicar_btn_tipo_de_documento",
  (
    botao_tipo_de_documento,
    nome_tabela_edicao = tipo_de_documento_locators.tbl_tipo_de_documento()
  ) => {
    switch (botao_tipo_de_documento) {
      case "Salvar":
        cy.get(
          tipo_de_documento_locators.btn_salvar_tipo_de_documento()
        ).click();
        break;
      case "Filtrar":
        cy.get(
          tipo_de_documento_locators.btn_filtrar_tipo_de_documento()
        ).click();
        break;
      case "Editar":
        cy.get(
          commons_locators.tbl_nome_todas_consultas_edicao(nome_tabela_edicao)
        )
          .find(tipo_de_documento_locators.btn_editar_tipo_documento())
          .click();
        break;
      case "Excluir":
        cy.get(tipo_de_documento_locators.btn_excluir_tipo_documento()).click();
        break;
      case "Confirmar Excluir":
        cy.get(
          tipo_de_documento_locators.btn_confirmacao_excluir_tipo_documento()
        ).click();
        break;

      default:
        break;
    }
  }
);

Cypress.Commands.add(
  "informar_dados_filtro_por_nome_tipo_de_documento",
  (filtrar_por_nome) => {
    cy.get(
      tipo_de_documento_locators.txt_filtrar_por_nome_tipo_de_documento()
    ).type(filtrar_por_nome);
  }
);
