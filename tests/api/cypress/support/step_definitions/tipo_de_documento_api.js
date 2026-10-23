import { Given, When, Then } from "cypress-cucumber-preprocessor/steps";

const Dado = Given;
const Quando = When;
const Entao = Then;

Dado("crio o tipo de documento com o nome de {string} via API", (nome) => {
  return cy.criar_tipo_de_documento(nome);
});

Entao("excluo o tipo de documento com o nome de {string} via API", (nome) => {
  return cy.excluir_tipo_de_documento_por_nome(nome);
});

Entao("excluo e confirmo o tipo de documento com o nome de {string} via API", (nome) => {
  return cy.excluir_tipo_de_documento_por_nome(nome, { exigirExistencia: true });
});

Entao("confirmo que o tipo de documento com o nome de {string} não existe via API", (nome) => {
  return cy.confirmar_tipo_de_documento_ausente(nome);
});

Entao("confirmo que existe exatamente um tipo de documento com o nome de {string} via API", (nome) => {
  return cy.confirmar_tipo_de_documento_existente(nome);
});
