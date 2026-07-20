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

Cypress.Commands.add("cadastrar_fornecedor", (nome, cpf_cnpj) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
      body: {
        nome,
        cpf_cnpj: `${cpf_cnpj}`,
      },
    });
  });
});

Cypress.Commands.add("excluir_fornecedor_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
      qs: {
        nome,
      },
    }).then((response) => {
      const fornecedor = Array.isArray(response.body)
        ? response.body[0]
        : undefined;
      if (!fornecedor) {
        return cy.wrap({ status: 404, body: [] });
      }

      return requestWithToken(token, {
        method: "DELETE",
        url:
          Cypress.config("baseUrlPTRFHomol") +
          "api/fornecedores/" +
          fornecedor.id +
          "/",
      });
    });
  });
});
