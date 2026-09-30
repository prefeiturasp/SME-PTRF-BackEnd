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

const obterFornecedores = (body) =>
  Array.isArray(body) ? body : body.results || [];

const formatarCpfCnpj = (cpfCnpj) => {
  const numeros = String(cpfCnpj).replace(/\D/g, "");

  if (numeros.length === 11) {
    return numeros.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  }

  if (numeros.length === 14) {
    return numeros.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      "$1.$2.$3/$4-$5",
    );
  }

  return cpfCnpj;
};

Cypress.Commands.add("criar_fornecedor", (nome, cpfCnpj) => {
  return cy.gerar_token().then((token) => {
    const cpfCnpjFormatado = formatarCpfCnpj(cpfCnpj);

    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
      qs: { cpf_cnpj: cpfCnpjFormatado },
    }).then((response) => {
      expect(response.status, `consulta do CPF/CNPJ "${cpfCnpjFormatado}"`).to
        .eq(200);

      const fornecedores = obterFornecedores(response.body).filter(
        (fornecedor) => fornecedor.cpf_cnpj === cpfCnpjFormatado,
      );

      return fornecedores
        .reduce((chain, fornecedor) => {
          return chain.then(() => {
            return requestWithToken(token, {
              method: "DELETE",
              url:
                Cypress.config("baseUrlPTRFHomol") +
                `api/fornecedores/${fornecedor.id}/`,
            }).then((deleteResponse) => {
              expect(
                deleteResponse.status,
                `exclusao do fornecedor ${fornecedor.id}: ${JSON.stringify(deleteResponse.body)}`,
              ).to.eq(204);
            });
          });
        }, cy.wrap(null, { log: false }))
        .then(() => {
          return requestWithToken(token, {
            method: "POST",
            url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
            body: {
              nome,
              cpf_cnpj: cpfCnpjFormatado,
            },
          }).then((createResponse) => {
            expect(
              createResponse.status,
              `cadastro do fornecedor "${nome}": ${JSON.stringify(createResponse.body)}`,
            ).to.eq(201);
            expect(createResponse.body.nome).to.eq(nome);
            expect(createResponse.body.cpf_cnpj).to.eq(cpfCnpjFormatado);
            expect(
              createResponse.body.uuid || createResponse.body.id,
              "identificador do fornecedor criado",
            ).to.exist;

            return requestWithToken(token, {
              method: "GET",
              url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
              qs: { cpf_cnpj: cpfCnpjFormatado },
            }).then((getResponse) => {
              expect(getResponse.status, "consulta após criar fornecedor").to.eq(
                200,
              );

              const fornecedoresCriados = obterFornecedores(
                getResponse.body,
              ).filter(
                (fornecedor) =>
                  fornecedor.nome === nome &&
                  fornecedor.cpf_cnpj === cpfCnpjFormatado,
              );

              expect(
                fornecedoresCriados,
                "fornecedor persistido após o POST",
              ).to.have.length(1);
              return createResponse;
            });
          });
        });
    });
  });
});

Cypress.Commands.add(
  "excluir_fornecedor_por_nome",
  (nome, { exigirExistencia = false } = {}) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
      qs: { nome },
    }).then((response) => {
      expect(response.status, `consulta do fornecedor "${nome}"`).to.eq(200);

      const fornecedores = obterFornecedores(response.body).filter(
        (fornecedor) => fornecedor.nome === nome,
      );

      if (!fornecedores.length) {
        expect(
          exigirExistencia,
          `fornecedor "${nome}" deveria existir antes da exclusão`,
        ).to.eq(false);
        return cy.wrap({ status: 404, body: [] }, { log: false });
      }

      return fornecedores.reduce((chain, fornecedor) => {
        return chain.then(() => {
          return requestWithToken(token, {
            method: "DELETE",
            url:
              Cypress.config("baseUrlPTRFHomol") +
              `api/fornecedores/${fornecedor.id}/`,
          }).then((deleteResponse) => {
            expect(
              deleteResponse.status,
              `exclusao do fornecedor ${fornecedor.id}: ${JSON.stringify(deleteResponse.body)}`,
            ).to.eq(204);
            return deleteResponse;
          });
        });
      }, cy.wrap(null, { log: false })).then((deleteResponse) => {
        return requestWithToken(token, {
          method: "GET",
          url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
          qs: { nome },
        }).then((confirmationResponse) => {
          expect(
            confirmationResponse.status,
            "consulta após excluir fornecedor",
          ).to.eq(200);

          const fornecedoresRestantes = obterFornecedores(
            confirmationResponse.body,
          ).filter((fornecedor) => fornecedor.nome === nome);

          expect(
            fornecedoresRestantes,
            `ausência do fornecedor "${nome}" após o DELETE`,
          ).to.be.empty;
          return deleteResponse;
        });
      });
    });
  });
  },
);

Cypress.Commands.add("confirmar_fornecedor_ausente", (nome) => {
  return cy.gerar_token().then((token) => {
    return requestWithToken(token, {
      method: "GET",
      url: Cypress.config("baseUrlPTRFHomol") + "api/fornecedores/",
      qs: { nome },
    }).then((response) => {
      expect(response.status, `consulta do fornecedor "${nome}"`).to.eq(200);

      const fornecedores = obterFornecedores(response.body).filter(
        (fornecedor) => fornecedor.nome === nome,
      );

      expect(fornecedores, `ausência do fornecedor "${nome}"`).to.be.empty;
      return response;
    });
  });
});
