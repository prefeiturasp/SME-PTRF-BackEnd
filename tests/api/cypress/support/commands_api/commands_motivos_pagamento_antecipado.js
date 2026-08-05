/// <reference types='cypress' />

const requestWithToken = (token, options) => {
  return cy.request({
    ...options,
    headers: {
      Authorization: `JWT ${token}`,
      ...(options.headers || {}),
    },
    failOnStatusCode: false,
  });
};

Cypress.Commands.add("cadastrar_motivo_pagamento_antecipado", (motivo) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url:
        Cypress.config("baseUrlPTRFHomol") +
        `api/motivos-pagamento-antecipado/`,
      body: {
        motivo,
      },
    });
  });
});

Cypress.Commands.add(
  "excluir_motivo_pagamento_antecipado_por_motivo",
  (motivo) => {
    return cy.gerar_token().then((token) => {
      return requestWithToken(token, {
        method: "GET",
        url:
          Cypress.config("baseUrlPTRFHomol") +
          `api/motivos-pagamento-antecipado/`,
        qs: {
          motivo,
        },
      }).then((response) => {
        const item = Array.isArray(response.body)
          ? response.body[0]
          : undefined;
        if (!item) {
          return cy.wrap({ status: 404, body: [] });
        }

        return requestWithToken(token, {
          method: "DELETE",
          url:
            Cypress.config("baseUrlPTRFHomol") +
            `api/motivos-pagamento-antecipado/${item.uuid}/`,
        });
      });
    });
  },
);
