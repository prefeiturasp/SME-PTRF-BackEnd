/// <reference types='cypress' />

describe("Validar rotas de acoes da aplicação SigEscola", () => {
  var usuario = Cypress.config("usuario_homol_sme");
  var senha = Cypress.config("senha_homol");
  before(() => {
    cy.autenticar_login(usuario, senha);
  });

  context("Casos de teste para a rota de Post api/acoes-associacoes/", () => {

    it("Validar Post no endpoint api/acoes-associacoes/ com sucesso", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
          expect(responseExclusao.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com vínculo duplicado", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
        expect(responseCadastro.status).to.eq(201);
        cy.cadastrar_acoes_associacoes(body).then((responseDuplicado) => {
          expect(responseDuplicado.status).to.eq(400);
        });
        cy.excluir_acoes_associacoes(responseCadastro.body.uuid);
      });
    });
  });

  context("Casos de teste para a rota de Put api/acoes-associacoes/{uuid}/", () => {

    it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com uuid inexistente", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "ATIVA",
      };
      var id = "11111111-2222-3333-4444-555555555555";
      cy.editar_acoes_associacoes(body, id).then((response) => {
        expect(response.status).to.eq(404);
      });
    });
  });

  context("Casos de teste para a rota de Patch api/acoes-associacoes/{uuid}/", () => {

    it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com uuid inexistente", () => {
      var body = {
        status: "INATIVA",
      };
      var id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee";
      cy.alterar_acoes_associacoes(body, id).then((response) => {
        expect(response.status).to.eq(404);
      });
    });
  });

  context("Casos de teste para a rota de Get api/acoes-associacoes/", () => {

    it("Validar Get no endpoint api/acoes-associacoes/ sem filtros", () => {
      var id = "";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ apenas com status ATIVA", () => {
      var id = "?status=ATIVA";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ apenas com acao uuid", () => {
      var id = "?acao__uuid=82a4bd9a-5884-4a43-9ae9-4fee0855f9b7";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
      });
    });
  });

  context("Casos de teste para a rota de Get /api/acoes-associacoes/{uuid}/obter-saldo-atual/", () => {

    it("Validar Get obter-saldo-atual com uuid inexistente porém válido", () => {
      var id = "99999999-8888-7777-6666-555555555555";
      cy.validar_acoes_associacoes_obter_saldo_atual(id).then((response) => {
        expect(response.status).to.eq(404);
      });
    });
  });
});
