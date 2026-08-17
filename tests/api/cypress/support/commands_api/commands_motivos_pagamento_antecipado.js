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

Cypress.Commands.add("criar_motivo_pagamento_antecipado", (motivo) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url:
        Cypress.config("baseUrlPTRFHomol") +
        "api/motivos-pagamento-antecipado/",
      body: { motivo },
    }).then((response) => {
      expect(
        response.status,
        `cadastro do motivo de pagamento antecipado "${motivo}": ${JSON.stringify(response.body)}`,
      ).to.eq(201);
      return response;
    });
  });
});

Cypress.Commands.add(
  "excluir_motivo_pagamento_antecipado_por_nome",
  (motivo) => {
    return cy.gerar_token().then((token) => {
      return requestWithToken(token, {
        method: "GET",
        url:
          Cypress.config("baseUrlPTRFHomol") +
          "api/motivos-pagamento-antecipado/",
        qs: { motivo },
      }).then((response) => {
        expect(
          response.status,
          `consulta do motivo de pagamento antecipado "${motivo}"`,
        ).to.eq(200);

        const motivoNormalizado = motivo.toLocaleLowerCase("pt-BR");
        const motivos = (Array.isArray(response.body)
          ? response.body
          : response.body.results || []
        ).filter(
          (item) =>
            item.motivo.toLocaleLowerCase("pt-BR") === motivoNormalizado,
        );

        if (!motivos.length) {
          return cy.wrap({ status: 404, body: [] }, { log: false });
        }

        return motivos.reduce((chain, item) => {
          return chain.then(() => {
            return requestWithToken(token, {
              method: "DELETE",
              url:
                Cypress.config("baseUrlPTRFHomol") +
                `api/motivos-pagamento-antecipado/${item.uuid}/`,
            }).then((deleteResponse) => {
              expect(
                deleteResponse.status,
                `exclusao do motivo ${item.uuid}: ${JSON.stringify(deleteResponse.body)}`,
              ).to.eq(204);
              return deleteResponse;
            });
          });
        }, cy.wrap(null, { log: false }));
      });
    });
  },
);
