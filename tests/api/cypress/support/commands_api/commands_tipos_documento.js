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

Cypress.Commands.add("cadastrar_tipo_do_documento", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-documento/`,
      body: {
        nome,
        apenas_digitos: true,
        numero_documento_digitado: true,
        eh_documento_de_retencao_de_imposto: true,
        pode_reter_imposto: true,
        documento_comprobatorio_de_despesa: true,
      },
    });
  });
});

Cypress.Commands.add("excluir_tipo_do_documento_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-documento/`,
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
          `api/tipos-documento/${tipo.uuid}/`,
      });
    });
  });
});
