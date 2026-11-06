/// <reference types='cypress' />

const requestWithToken = (token, options) => {
  return cy.request({
    ...options,
    headers: {
      Authorization: `JWT ${token}`,
      ...(options.headers || {}),
    },
    failOnStatusCode: false,
    log: false,
  });
};

const obterTipos = (body) =>
  Array.isArray(body) ? body : body.results || [];

const consultarTiposPorNome = (token, nome) =>
  requestWithToken(token, {
    method: "GET",
    url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-conta/",
    qs: { nome },
  }).then((response) => {
    expect(response.status, `consulta do tipo de conta "${nome}"`).to.eq(200);
    const tipos = obterTipos(response.body).filter((item) => item.nome === nome);
    return { response, tipos };
  });

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
        expect(createResponse.body, "corpo da criação do tipo de conta").to.include({
          nome,
          agencia: "0001",
          banco_nome: "teste automatizado",
          numero_cartao: "1234432112344321",
          numero_conta: "12345",
          apenas_leitura: true,
          permite_inativacao: true,
        });
        expect(createResponse.body.uuid || createResponse.body.id, "identificador do tipo de conta")
          .to.exist;

        return consultarTiposPorNome(token, nome).then(({ tipos }) => {
          expect(tipos, `tipo de conta "${nome}" persistido`).to.have.length(1);
          expect(tipos[0]).to.include({ nome });
          return createResponse;
        });
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

Cypress.Commands.add("excluir_tipo_de_conta_por_nome", (nome, { exigirExistencia = false } = {}) => {
  return cy.gerar_token().then((token) => {
    return consultarTiposPorNome(token, nome).then(({ tipos }) => {
      if (exigirExistencia) {
        expect(tipos, `tipo de conta "${nome}" existente antes da exclusão`)
          .not.to.be.empty;
      }

      if (!tipos.length) {
        return cy.wrap({ status: 404, body: [] }, { log: false });
      }

      return tipos.reduce((chain, tipo) => chain.then(() =>
        requestWithToken(token, {
          method: "DELETE",
          url: Cypress.config("baseUrlPTRFHomol") + `api/tipos-conta/${tipo.uuid}/`,
        }).then((deleteResponse) => {
          expect(
            deleteResponse.status,
            `exclusão do tipo de conta ${tipo.uuid}: ${JSON.stringify(deleteResponse.body)}`,
          ).to.eq(204);
        })
      ), cy.wrap(null, { log: false })).then(() =>
        consultarTiposPorNome(token, nome).then(({ tipos: tiposRestantes }) => {
          expect(tiposRestantes, `tipo de conta "${nome}" ausente após exclusão`)
            .to.be.empty;
        })
      );
    });
  });
});

Cypress.Commands.add("confirmar_tipo_de_conta_ausente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposPorNome(token, nome).then(({ tipos }) => {
      expect(tipos, `tipo de conta "${nome}" ausente`).to.be.empty;
    })
  );
});

Cypress.Commands.add("confirmar_tipo_de_conta_existente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposPorNome(token, nome).then(({ tipos }) => {
      expect(tipos, `um único tipo de conta "${nome}" existente`).to.have.length(1);
      return tipos[0];
    })
  );
});
