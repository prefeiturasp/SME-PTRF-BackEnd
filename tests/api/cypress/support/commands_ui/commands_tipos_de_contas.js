import Tipo_de_conta_Localizadores from "../locators/tipo_de_conta_locators";
import Commons_Locators from "../locators/commons_locators";

const commons_locators = new Commons_Locators();
const tipo_de_conta_Localizadores = new Tipo_de_conta_Localizadores();

const preencherCampoSeExistir = (seletor, valor) => {
  cy.get("body").then(($body) => {
    if ($body.find(seletor).length) {
      cy.get(seletor).should("be.visible").clear().type(valor);
    }
  });
};

const ajustarCheckboxSeExistir = (seletor, deveEstarMarcado) => {
  cy.get("body").then(($body) => {
    if ($body.find(seletor).length) {
      cy.get(seletor).then(($checkbox) => {
        if ($checkbox.prop("checked") !== deveEstarMarcado) {
          cy.wrap($checkbox).click();
        }
      });
    }
  });
};

Cypress.Commands.add(
  "clicar_btn_adicionar_tipo_de_conta",
  (btn_tipo_conta, nome_tabela_edicao) => {
    switch (btn_tipo_conta) {
      case "Adicionar tipo de conta":
        cy.get(
          tipo_de_conta_Localizadores.btn_adicionar_tipo_de_conta()
        , { timeout: 30000 }).should("be.visible").click();
        break;
      case "Salvar":
        cy.get(tipo_de_conta_Localizadores.btn_salvar(), { timeout: 30000 }).should("be.visible").click();
        break;
      case "Editar":
        cy.get(
          tipo_de_conta_Localizadores.tbl_resultados_da_consulta(
            nome_tabela_edicao
          ),
          { timeout: 30000 }
        )
          .should("be.visible")
          .find(tipo_de_conta_Localizadores.btn_editar())
          .click();
        break;
      case "Apagar tipo de conta":
        cy.get(tipo_de_conta_Localizadores.btn_apagar_tipo_conta(), { timeout: 30000 }).should("be.visible").click();
        break;
      case "Excluir":
        cy.get(".ant-modal-content", { timeout: 30000 })
          .should("be.visible")
          .within(() => {
            cy.contains("button", "Excluir").click();
          });
        break;
      case "Pesquisar":
        cy.contains("button", "Filtrar", { timeout: 30000 })
          .should("be.visible")
          .and("not.be.disabled")
          .click();
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
    cy.get(tipo_de_conta_Localizadores.txt_nome_do_tipo_de_conta(), { timeout: 30000 }).should("be.visible").clear();
    nome_do_tipo_de_conta
      ? cy
          .get(tipo_de_conta_Localizadores.txt_nome_do_tipo_de_conta())
          .type(nome_do_tipo_de_conta)
      : "";
    preencherCampoSeExistir(
      tipo_de_conta_Localizadores.txt_nome_do_banco(),
      nome_do_banco
    );
    preencherCampoSeExistir(
      tipo_de_conta_Localizadores.txt_n_da_agencia(),
      n_da_agencia
    );
    preencherCampoSeExistir(
      tipo_de_conta_Localizadores.txt_n_da_conta(),
      n_da_conta
    );
    preencherCampoSeExistir(
      tipo_de_conta_Localizadores.txt_n_do_cartao(),
      n_do_cartao
    );
    ajustarCheckboxSeExistir(
      tipo_de_conta_Localizadores.chk_exibir_os_dados_da_conta_somente_leitura(),
      exibir_os_dados_da_conta_somente_leitura === "true"
    );
    ajustarCheckboxSeExistir(
      tipo_de_conta_Localizadores.chk_conta_permite_encerramento(),
      conta_permite_encerramento === "true"
    );
  }
);

Cypress.Commands.add(
  "validar_mensagem_de_exclusao_tipo_de_conta",
  (mensagem_de_confirmacao_de_erro) => {
    cy.contains(mensagem_de_confirmacao_de_erro, { timeout: 30000 })
      .should("be.visible");
  }
);

Cypress.Commands.add(
  "informar_dados_consulta_tipo_conta",
  (dados_da_pesquisa) => {
    cy.contains(/Exibindo \d+ tipo\(s\) de conta\(s\)/, { timeout: 30000 })
      .should("be.visible");
    cy.get(tipo_de_conta_Localizadores.txt_pesquisar(), { timeout: 30000 })
      .should("be.visible")
      .and("not.be.disabled");
    cy.wait(500, { log: false });
    cy.get(tipo_de_conta_Localizadores.txt_pesquisar()).clear();
    cy.get(tipo_de_conta_Localizadores.txt_pesquisar()).type(dados_da_pesquisa);
  }
);

Cypress.Commands.add(
  "validar_resultado_da_consulta_tipo_conta",
  (valores_consulta) => {
    cy.contains(valores_consulta, { timeout: 30000 }).should("be.visible");
  }
);
