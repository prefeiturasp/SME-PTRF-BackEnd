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

Cypress.Commands.add("cadastrar_tipo_de_transacao", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-transacao/`,
      body: {
        nome,
        tem_documento: true,
      },
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_transacao_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-transacao/`,
      qs: {
        nome,
      },
    }).then((response) => {
      const tipo = Array.isArray(response.body) ? response.body[0] : undefined;
      if (!tipo) {
        return cy.wrap({ status: 404, body: [] });
      }

      return requestWithToken(token, {
        method: "DELETE",
        url:
          Cypress.config("baseUrlPTRFHomol") +
          `api/tipos-transacao/${tipo.uuid}/`,
      });
    });
  });
});
