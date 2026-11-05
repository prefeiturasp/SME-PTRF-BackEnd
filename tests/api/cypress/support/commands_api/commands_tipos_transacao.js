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

const obterTiposTransacao = (body) =>
  Array.isArray(body) ? body : body.results || [];

const normalizarNome = (nome) => nome.toLocaleLowerCase("pt-BR");

const consultarTiposTransacaoPorNome = (token, nome) =>
  requestWithToken(token, {
    method: "GET",
    url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-transacao/",
    qs: { nome },
  }).then((response) => {
    expect(response.status, `consulta do tipo de transacao "${nome}"`).to.eq(200);
    const nomeNormalizado = normalizarNome(nome);
    const tiposTransacao = obterTiposTransacao(response.body).filter(
      (item) => normalizarNome(item.nome) === nomeNormalizado,
    );
    return { response, tiposTransacao };
  });

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
      expect(response.body, "corpo da criacao do tipo de transacao").to.include({
        nome,
        tem_documento: true,
      });
      expect(
        response.body.uuid || response.body.id,
        "identificador do tipo de transacao",
      ).to.exist;

      return consultarTiposTransacaoPorNome(token, nome).then(
        ({ tiposTransacao }) => {
          expect(
            tiposTransacao,
            `tipo de transacao "${nome}" persistido`,
          ).to.have.length(1);
          return response;
        },
      );
    });
  });
});

Cypress.Commands.add(
  "excluir_tipo_de_transacao_por_nome",
  (nome, { exigirExistencia = false } = {}) => {
    return cy.gerar_token().then((token) => {
      return consultarTiposTransacaoPorNome(token, nome).then(
        ({ tiposTransacao }) => {
          if (exigirExistencia) {
            expect(
              tiposTransacao,
              `tipo de transacao "${nome}" existente antes da exclusao`,
            ).not.to.be.empty;
          }

          if (!tiposTransacao.length) {
            return cy.wrap({ status: 404, body: [] }, { log: false });
          }

          return tiposTransacao
            .reduce((chain, tipoTransacao) => {
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
            }, cy.wrap(null, { log: false }))
            .then(() =>
              consultarTiposTransacaoPorNome(token, nome).then(
                ({ tiposTransacao: restantes }) => {
                  expect(
                    restantes,
                    `tipo de transacao "${nome}" ausente apos exclusao`,
                  ).to.be.empty;
                },
              ),
            );
        },
      );
    });
  },
);

Cypress.Commands.add("confirmar_tipo_de_transacao_ausente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposTransacaoPorNome(token, nome).then(({ tiposTransacao }) => {
      expect(tiposTransacao, `tipo de transacao "${nome}" ausente`).to.be.empty;
    }),
  );
});

Cypress.Commands.add("confirmar_tipo_de_transacao_existente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposTransacaoPorNome(token, nome).then(({ tiposTransacao }) => {
      expect(
        tiposTransacao,
        `um unico tipo de transacao "${nome}" existente`,
      ).to.have.length(1);
      return tiposTransacao[0];
    }),
  );
});
