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

const obterMotivos = (body) =>
  Array.isArray(body) ? body : body.results || [];

const normalizarMotivo = (motivo) => motivo.toLocaleLowerCase("pt-BR");

const consultarMotivosPorNome = (token, motivo) =>
  requestWithToken(token, {
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

    const motivoNormalizado = normalizarMotivo(motivo);
    const motivos = obterMotivos(response.body).filter(
      (item) => normalizarMotivo(item.motivo) === motivoNormalizado,
    );

    return { response, motivos };
  });

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
      expect(response.body, "corpo da criação do motivo").to.include({ motivo });
      expect(response.body.uuid || response.body.id, "identificador do motivo")
        .to.exist;

      return consultarMotivosPorNome(token, motivo).then(({ motivos }) => {
        expect(motivos, `motivo "${motivo}" persistido`).to.have.length(1);
        expect(motivos[0].motivo).to.eq(motivo);
        return response;
      });
    });
  });
});

Cypress.Commands.add(
  "excluir_motivo_pagamento_antecipado_por_nome",
  (motivo, { exigirExistencia = false } = {}) => {
    return cy.gerar_token().then((token) => {
      return consultarMotivosPorNome(token, motivo).then(({ motivos }) => {
        if (exigirExistencia) {
          expect(motivos, `motivo "${motivo}" existente antes da exclusão`)
            .not.to.be.empty;
        }

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
        }, cy.wrap(null, { log: false })).then(() => {
          return consultarMotivosPorNome(token, motivo).then(
            ({ motivos: motivosRestantes }) => {
              expect(motivosRestantes, `motivo "${motivo}" ausente após exclusão`)
                .to.be.empty;
            },
          );
        });
      });
    });
  },
);

Cypress.Commands.add("confirmar_motivo_pagamento_antecipado_ausente", (motivo) => {
  return cy.gerar_token().then((token) => {
    return consultarMotivosPorNome(token, motivo).then(({ motivos }) => {
      expect(motivos, `motivo "${motivo}" ausente`).to.be.empty;
    });
  });
});

Cypress.Commands.add("confirmar_motivo_pagamento_antecipado_existente", (motivo) => {
  return cy.gerar_token().then((token) => {
    return consultarMotivosPorNome(token, motivo).then(({ motivos }) => {
      expect(motivos, `um único motivo "${motivo}" existente`).to.have.length(1);
      expect(motivos[0].motivo).to.eq(motivo);
      return motivos[0];
    });
  });
});
