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

const obterTiposDocumento = (body) =>
  Array.isArray(body) ? body : body.results || [];

const normalizarNome = (nome) => nome.toLocaleLowerCase("pt-BR");

const consultarTiposDocumentoPorNome = (token, nome) =>
  requestWithToken(token, {
    method: "GET",
    url: Cypress.config("baseUrlPTRFHomol") + "api/tipos-documento/",
    qs: { nome },
  }).then((response) => {
    expect(response.status, `consulta do tipo de documento "${nome}"`).to.eq(200);
    const nomeNormalizado = normalizarNome(nome);
    const tiposDocumento = obterTiposDocumento(response.body).filter(
      (item) => normalizarNome(item.nome) === nomeNormalizado,
    );
    return { response, tiposDocumento };
  });

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
      expect(response.body, "corpo da criação do tipo de documento").to.include({
        nome,
        apenas_digitos: true,
        numero_documento_digitado: true,
        pode_reter_imposto: true,
        eh_documento_de_retencao_de_imposto: true,
        documento_comprobatorio_de_despesa: true,
      });
      expect(response.body.uuid || response.body.id, "identificador do tipo de documento")
        .to.exist;

      return consultarTiposDocumentoPorNome(token, nome).then(({ tiposDocumento }) => {
        expect(tiposDocumento, `tipo de documento "${nome}" persistido`).to.have.length(1);
        return response;
      });
    });
  });
});

Cypress.Commands.add("excluir_tipo_de_documento_por_nome", (nome, { exigirExistencia = false } = {}) => {
  return cy.gerar_token().then((token) => {
    return consultarTiposDocumentoPorNome(token, nome).then(({ tiposDocumento }) => {
      if (exigirExistencia) {
        expect(tiposDocumento, `tipo de documento "${nome}" existente antes da exclusão`)
          .not.to.be.empty;
      }

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
      }, cy.wrap(null, { log: false })).then(() =>
        consultarTiposDocumentoPorNome(token, nome).then(({ tiposDocumento: restantes }) => {
          expect(restantes, `tipo de documento "${nome}" ausente após exclusão`).to.be.empty;
        })
      );
    });
  });
});

Cypress.Commands.add("confirmar_tipo_de_documento_ausente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposDocumentoPorNome(token, nome).then(({ tiposDocumento }) => {
      expect(tiposDocumento, `tipo de documento "${nome}" ausente`).to.be.empty;
    })
  );
});

Cypress.Commands.add("confirmar_tipo_de_documento_existente", (nome) => {
  return cy.gerar_token().then((token) =>
    consultarTiposDocumentoPorNome(token, nome).then(({ tiposDocumento }) => {
      expect(tiposDocumento, `um único tipo de documento "${nome}" existente`).to.have.length(1);
      return tiposDocumento[0];
    })
  );
});
