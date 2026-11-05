/// <reference types='cypress' />

import "@shelex/cypress-allure-plugin";
import "cypress-cloud/support";
import "../../../../support/commands_api/commands_login";
import "../../../../support/commands_api/commands_usuarios_me";

// Erros de transporte do Cypress podem incluir headers e corpo do login.
Cypress.on("fail", (error) => {
  if (/cy\.request\(\)/.test(error.message)) {
    throw new Error(
      "Falha na requisição HTTP. Headers, corpo e credenciais omitidos do relatório.",
    );
  }
  throw error;
});

describe("GET /api/usuarios/me/", { retries: 0 }, () => {
  beforeEach(() => {
    Cypress.env("token_api_sme", null);
    cy.clearAllCookies({ log: false });
  });

  const json = (response, codigo) => {
    expect(response.status).to.eq(codigo);
    expect(response.headers["content-type"]).to.match(
      /^application\/json(?:;|$)/,
    );
  };

  const payloadJwt = (token) => {
    try {
      const partes = token.split(".");
      if (partes.length !== 3 || !partes[2]) throw new Error();
      const base64 = partes[1].replace(/-/g, "+").replace(/_/g, "/");
      return JSON.parse(
        atob(base64.padEnd(Math.ceil(base64.length / 4) * 4, "=")),
      );
    } catch (_) {
      throw new Error(
        "A credencial fornecida não contém um payload JWT legível; valor omitido.",
      );
    }
  };

  const autenticado = () => {
    expect(
      Boolean(Cypress.config("usuario_homol_sme")),
      "usuário de teste configurado",
    ).to.eq(true);
    expect(
      Boolean(Cypress.config("senha_homol")),
      "senha de teste configurada",
    ).to.eq(true);
    return cy.gerar_token(0);
  };

  const identidade = (response, token) => {
    json(response, 200);
    const payload = payloadJwt(token);
    expect(
      Number.isInteger(payload.user_id),
      "login fornece user_id inteiro",
    ).to.eq(true);
    expect(
      response.body.id === payload.user_id,
      "id corresponde ao token emitido no login",
    ).to.eq(true);
    expect(
      response.body.username === Cypress.config("usuario_homol_sme"),
      "username corresponde à credencial configurada",
    ).to.eq(true);
  };

  // Corpo definido por JWTAuthentication/SimpleJWT 5.4.0, com idioma fixado em inglês.
  const tokenRejeitado = (response) => {
    json(response, 401);
    expect(response.body).to.deep.eq({
      detail: "Given token not valid for any token type",
      code: "token_not_valid",
      messages: [
        {
          token_class: "AccessToken",
          token_type: "access",
          message: "Token is invalid or expired",
        },
      ],
    });
  };

  it("CT01 — autenticação válida retorna os dados da conta utilizada", () => {
    autenticado().then((token) => {
      cy.consultar_usuarios_me("JWT " + token).then((response) =>
        identidade(response, token),
      );
    });
  });

  it("CT02 — id e username correspondem ao login, independentemente da resposta avaliada", () => {
    autenticado().then((token) => {
      cy.consultar_usuarios_me("JWT " + token).then((response) =>
        identidade(response, token),
      );
    });
  });

  it("CT03 — ausência de autenticação retorna 401 sem dados pessoais", () => {
    cy.consultar_usuarios_me().then((response) => {
      json(response, 401);
      expect(response.body).to.deep.eq({
        detail: "Authentication credentials were not provided.",
      });
    });
  });

  it("CT04 — credencial inválida retorna o erro exato de token", () => {
    // Valor sintético sem estrutura JWT, sem depender de uma credencial válida.
    cy.consultar_usuarios_me("JWT " + globalThis.crypto.randomUUID()).then(
      tokenRejeitado,
    );
  });
});
