import { Given, When, Then } from "cypress-cucumber-preprocessor/steps";

const Dado = Given;
const Quando = When;
const Entao = Then;

Dado("crio o tipo de transacao com o nome de {string} via API", (nome) => {
  cy.criar_tipo_de_transacao(nome);
});

Entao("excluo o tipo de transacao com o nome de {string} via API", (nome) => {
  cy.excluir_tipo_de_transacao_por_nome(nome);
});
