import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given(
  "crio o fornecedor com o nome {string} e {string} via API",
  (nome, cpfCnpj) => {
    cy.criar_fornecedor(nome, cpfCnpj);
  },
);

Then("excluo o fornecedor com o nome {string} via API", (nome) => {
  cy.excluir_fornecedor_por_nome(nome);
});
