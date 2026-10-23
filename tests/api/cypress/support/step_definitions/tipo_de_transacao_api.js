import { Given, When, Then } from "cypress-cucumber-preprocessor/steps";

const Dado = Given;
const Quando = When;
const Entao = Then;

Dado("crio o tipo de transacao com o nome de {string} via API", (nome) => {
  return cy.criar_tipo_de_transacao(nome);
});

Entao("excluo o tipo de transacao com o nome de {string} via API", (nome) => {
  return cy.excluir_tipo_de_transacao_por_nome(nome);
});

Entao(
  "excluo e confirmo o tipo de transacao com o nome de {string} via API",
  (nome) => {
    return cy.excluir_tipo_de_transacao_por_nome(nome, {
      exigirExistencia: true,
    });
  },
);

Entao(
  "confirmo que o tipo de transacao com o nome de {string} nao existe via API",
  (nome) => {
    return cy.confirmar_tipo_de_transacao_ausente(nome);
  },
);

Entao(
  "confirmo que existe exatamente um tipo de transacao com o nome de {string} via API",
  (nome) => {
    return cy.confirmar_tipo_de_transacao_existente(nome);
  },
);
