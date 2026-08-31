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

Cypress.Commands.add("criar_tipo_de_documento", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "POST",
      url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-documento/",
      body: {
        nome,
        apenas_digitos: true,
        numero_documento_digitado: true,
        pode_reter_imposto: true,
        eh_documento_de_retencao_de_imposto: true,
        documento_comprobatorio_de_despesa: true,
      },
    }).then((response) => {
      expect(
        response.status,
        `cadastro do tipo de documento "${nome}": ${JSON.stringify(response.body)}`,
      ).to.eq(201);
      return response;
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_documento_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-documento/",
      qs: { nome },
    }).then((response) => {
      expect(response.status, `consulta do tipo de documento "${nome}"`).to.eq(
        200,
      );

      const nomeNormalizado = nome.toLocaleLowerCase("pt-BR");
      const tiposDocumento = (Array.isArray(response.body)
        ? response.body
        : response.body.results || []
      ).filter(
        (tipoDocumento) =>
          tipoDocumento.nome.toLocaleLowerCase("pt-BR") === nomeNormalizado,
      );

      if (!tiposDocumento.length) {
        return cy.wrap({ status: 404, body: [] }, { log: false });
      }

      return tiposDocumento.reduce((chain, tipoDocumento) => {
        return chain.then(() => {
          return requestWithToken(token, {
            method: "DELETE",
            url:
              Cypress.config("baseUrlPTRFHomol") +
              `api/tipos-documento/${tipoDocumento.uuid}/`,
          }).then((deleteResponse) => {
            expect(
              deleteResponse.status,
              `exclusao do tipo de documento ${tipoDocumento.uuid}: ${JSON.stringify(deleteResponse.body)}`,
            ).to.eq(204);
            return deleteResponse;
          });
        });
      }, cy.wrap(null, { log: false }));
    });
  });
});
