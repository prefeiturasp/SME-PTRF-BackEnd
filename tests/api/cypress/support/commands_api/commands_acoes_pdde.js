/// <reference types='cypress' />

Cypress.Commands.add("validar_acoes_pdde", (id) => {
  cy.request({
    method: "GET",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/acoes-pdde/${id}`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("cadastrar_acoes_pdde", (body) => {
  cy.request({
    method: "POST",
    url: Cypress.config("baseUrlPTRFHomol") + `api/acoes-pdde/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("excluir_acoes_pdde", (id) => {
  cy.request({
    method: "DELETE",
    url: Cypress.config("baseUrlPTRFHomol") + `api/acoes-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("alterar_acoes_pdde", (body, id) => {
  cy.request({
    method: "PUT",
    url: Cypress.config("baseUrlPTRFHomol") + `api/acoes-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("editar_acoes_pdde", (body, id) => {
  cy.request({
    method: "PATCH",
    url: Cypress.config("baseUrlPTRFHomol") + `api/acoes-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});
