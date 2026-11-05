import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given("crio o tipo conta com o nome {string} via API", (nome) => {
  return cy.cadastrar_tipo_de_conta(nome);
});

Then("excluo o tipo conta com o nome {string} via API", (nome) => {
  return cy.excluir_tipo_de_conta_por_nome(nome);
});

Then("excluo e confirmo o tipo conta com o nome {string} via API", (nome) => {
  return cy.excluir_tipo_de_conta_por_nome(nome, { exigirExistencia: true });
});

Then("confirmo que o tipo conta com o nome {string} não existe via API", (nome) => {
  return cy.confirmar_tipo_de_conta_ausente(nome);
});

Then("confirmo que existe exatamente um tipo conta com o nome {string} via API", (nome) => {
  return cy.confirmar_tipo_de_conta_existente(nome);
});
