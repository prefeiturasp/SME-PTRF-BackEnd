import Tipo_de_conta_Localizadores from "../locators/tipo_de_conta_locators";
import Commons_Locators from "../locators/commons_locators";

const commons_locators = new Commons_Locators();
const tipo_de_conta_Localizadores = new Tipo_de_conta_Localizadores();

Cypress.Commands.add(
  "clicar_btn_adicionar_tipo_de_conta",
  (btn_tipo_conta, nome_tabela_edicao) => {
    switch (btn_tipo_conta) {
      case "Adicionar tipo de conta":
        cy.get(
          tipo_de_conta_Localizadores.btn_adicionar_tipo_de_conta()
        ).click();
        break;
      case "Salvar":
        cy.get(tipo_de_conta_Localizadores.btn_salvar()).click();
        break;
      case "Editar":
        cy.get(
          tipo_de_conta_Localizadores.tbl_resultados_da_consulta(
            nome_tabela_edicao
          )
        )
          .find(tipo_de_conta_Localizadores.btn_editar())
          .click();
        break;
      case "Apagar tipo de conta":
        cy.get(tipo_de_conta_Localizadores.btn_apagar_tipo_conta()).click();
        break;
      case "Excluir":
        cy.get(tipo_de_conta_Localizadores.btn_excluir()).click();
        break;
      case "Pesquisar":
        cy.get(tipo_de_conta_Localizadores.btn_pesquisar()).click();
        break;
      default:
        break;
    }
  }
);

Cypress.Commands.add(
  "informar_dados_tipo_de_conta",
  (
    nome_do_tipo_de_conta,
    nome_do_banco,
    n_da_agencia,
    n_da_conta,
    n_do_cartao,
    exibir_os_dados_da_conta_somente_leitura,
    conta_permite_encerramento
  ) => {
    cy.get(tipo_de_conta_Localizadores.txt_nome_do_tipo_de_conta()).clear();
    nome_do_tipo_de_conta
      ? cy
          .get(tipo_de_conta_Localizadores.txt_nome_do_tipo_de_conta())
          .type(nome_do_tipo_de_conta)
      : "";
    cy.get(tipo_de_conta_Localizadores.txt_nome_do_banco())
      .clear()
      .type(nome_do_banco);
    cy.get(tipo_de_conta_Localizadores.txt_n_da_agencia())
      .clear()
      .type(n_da_agencia);
    cy.get(tipo_de_conta_Localizadores.txt_n_da_conta())
      .clear()
      .type(n_da_conta);
    cy.get(tipo_de_conta_Localizadores.txt_n_do_cartao())
      .clear()
      .type(n_do_cartao);
    if (exibir_os_dados_da_conta_somente_leitura == "true") {
      cy.get(
        tipo_de_conta_Localizadores.chk_exibir_os_dados_da_conta_somente_leitura()
      ).click();
    }
    if (conta_permite_encerramento == "true") {
      cy.get(
        tipo_de_conta_Localizadores.chk_conta_permite_encerramento()
      ).click();
    }
  }
);

Cypress.Commands.add(
  "validar_mensagem_de_exclusao_tipo_de_conta",
  (mensagem_de_confirmacao_de_erro) => {
    cy.get(commons_locators.msg_modal_confirmacao_exclusao())
      .should("be.visible")
      .and("contain", mensagem_de_confirmacao_de_erro);
  }
);

Cypress.Commands.add(
  "informar_dados_consulta_tipo_conta",
  (dados_da_pesquisa) => {
    cy.get(tipo_de_conta_Localizadores.txt_pesquisar()).type(dados_da_pesquisa);
  }
);

Cypress.Commands.add(
  "validar_resultado_da_consulta_tipo_conta",
  (valores_consulta) => {
    cy.get(tipo_de_conta_Localizadores.resultado_pesquisa_tipo_conta())
      .should("be.visible");
  }
);
