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

Cypress.Commands.add("cadastrar_tipo_de_conta", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + `api/recursos/`,
    }).then((response) => {
      expect(response.status, "consulta do recurso legado").to.eq(200);

      const recursos = Array.isArray(response.body)
        ? response.body
        : response.body.results || [];
      const recursoLegado = recursos.find((recurso) => recurso.legado);

      expect(recursoLegado, "recurso legado necessário ao tipo de conta").to
        .exist;

      return requestWithToken(token, {
        method: "POST",
        url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-conta/`,
        body: {
          nome,
          agencia: "0001",
          banco_nome: "teste automatizado",
          numero_cartao: "1234432112344321",
          numero_conta: "12345",
          apenas_leitura: true,
          permite_inativacao: true,
          recurso: recursoLegado.uuid,
        },
      }).then((createResponse) => {
        expect(
          createResponse.status,
          `cadastro do tipo de conta "${nome}": ${JSON.stringify(createResponse.body)}`,
        ).to.eq(201);
        return createResponse;
      });
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_conta_por_uuid", (uuid) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "DELETE",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-conta/${uuid}/`,
    }).then((response) => {
      expect(response.status, `exclusão do tipo de conta ${uuid}`).to.eq(204);
      return response;
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_conta_por_nome", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-conta/`,
      qs: {
        nome,
      },
    }).then((response) => {
      expect(response.status, `consulta do tipo de conta "${nome}"`).to.eq(200);

      const tipos = Array.isArray(response.body)
        ? response.body
        : response.body.results || [];
      const tipo = tipos.find((item) => item.nome === nome);

      if (!tipo) {
        return cy.wrap({ status: 404, body: [] }, { log: false });
      }

      return requestWithToken(token, {
        method: "DELETE",
        url:
          Cypress.config("baseUrlPTRFHomol") + `api/tipos-conta/${tipo.uuid}/`,
      }).then((deleteResponse) => {
        expect(
          deleteResponse.status,
          `exclusão do tipo de conta ${tipo.uuid}: ${JSON.stringify(deleteResponse.body)}`,
        ).to.eq(204);
        return deleteResponse;
      });
    });
  });
});
