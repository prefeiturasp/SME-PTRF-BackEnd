import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given("crio o tipo conta com o nome {string} via API", (nome) => {
  cy.cadastrar_tipo_de_conta(nome);
});

Then("excluo o tipo conta com o nome {string} via API", (nome) => {
  cy.excluir_tipo_de_conta_por_nome(nome);
});
