import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given(
  "crio o fornecedor com o nome {string} e {string} via API",
  (nome, cpfCnpj) => {
    return cy.criar_fornecedor(nome, cpfCnpj);
  },
);

Then("excluo o fornecedor com o nome {string} via API", (nome) => {
  return cy.excluir_fornecedor_por_nome(nome);
});

Then("excluo e confirmo o fornecedor com o nome {string} via API", (nome) => {
  return cy.excluir_fornecedor_por_nome(nome, { exigirExistencia: true });
});

Then("confirmo que o fornecedor com o nome {string} não existe via API", (nome) => {
  return cy.confirmar_fornecedor_ausente(nome);
});
