/// <reference types='cypress' />

Cypress.Commands.add("validar_programas_pdde", (id) => {
  cy.request({
    method: "GET",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/programas-pdde/${id}`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("cadastrar_programas_pdde", (body) => {
  cy.request({
    method: "POST",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/programas-pdde/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("excluir_programas_pdde", (id) => {
  cy.request({
    method: "DELETE",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/programas-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("alterar_programas_pdde", (body, id) => {
  cy.request({
    method: "PUT",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/programas-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});

Cypress.Commands.add("editar_programas_pdde", (body, id) => {
  cy.request({
    method: "PATCH",
    url: Cypress.config("baseUrlPTRFHomol") + `/api/programas-pdde/${id}/`,
    headers: {
      Authorization: "JWT " + globalThis.token,
    },
    body: body,
    failOnStatusCode: false,
  });
});
