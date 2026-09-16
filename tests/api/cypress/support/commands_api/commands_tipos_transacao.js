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

Cypress.Commands.add("criar_tipo_de_transacao", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-transacao/",
      body: { nome, tem_documento: true },
    }).then((response) => {
      expect(
        response.status,
        `cadastro do tipo de transacao "${nome}": ${JSON.stringify(response.body)}`,
      ).to.eq(201);
      return response;
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_transacao_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-transacao/",
      qs: { nome },
    }).then((response) => {
      expect(response.status, `consulta do tipo de transacao "${nome}"`).to.eq(
        200,
      );

      const nomeNormalizado = nome.toLocaleLowerCase("pt-BR");
      const tiposTransacao = (Array.isArray(response.body)
        ? response.body
        : response.body.results || []
      ).filter(
        (tipoTransacao) =>
          tipoTransacao.nome.toLocaleLowerCase("pt-BR") === nomeNormalizado,
      );

      if (!tiposTransacao.length) {
        return cy.wrap({ status: 404, body: [] }, { log: false });
      }

      return tiposTransacao.reduce((chain, tipoTransacao) => {
        return chain.then(() => {
          return requestWithToken(token, {
            method: "DELETE",
            url:
              Cypress.config("baseUrlPTRFHomol") +
              `api/tipos-transacao/${tipoTransacao.uuid}/`,
          }).then((deleteResponse) => {
            expect(
              deleteResponse.status,
              `exclusao do tipo de transacao ${tipoTransacao.uuid}: ${JSON.stringify(deleteResponse.body)}`,
            ).to.eq(204);
            return deleteResponse;
          });
        });
      }, cy.wrap(null, { log: false }));
    });
  });
});
