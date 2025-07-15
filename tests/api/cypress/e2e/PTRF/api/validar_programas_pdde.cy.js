/// <reference types='cypress' />

describe("Validar rotas de acoes da aplicação SigEscola", () => {
  var usuario = Cypress.config("usuario_homol_sme");
  var senha = Cypress.config("senha_homol");
  before(() => {
    cy.autenticar_login(usuario, senha);
  });

  context("Casos de teste para a rota de Get /api/programas-pdde/", () => {
    it("Validar Get no endpoint /api/programas-pdde/ com sucesso sem parametros", () => {
      var id = "";
      cy.validar_programas_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });

    it("Validar Get no endpoint /api/programas-pdde/ com sucesso e com todos parametros preenchidos paramentros", () => {
      var id = "?nome=Categoria%20PDDE%201&page=1&page_size=10";
      cy.validar_programas_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });

    it("Validar Get no endpoint /api/programas-pdde/ com sucesso e com paramentros de page e page size preenchidos", () => {
      var id = "?page=1&page_size=10";
      cy.validar_programas_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });

    it("Validar Get no endpoint /api/programas-pdde/ com sucesso e com paramentro de nome preenchido", () => {
      var id = "?nome=Categoria%20PDDE%201";
      cy.validar_programas_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });
  });

  context(
    "Casos de teste para a rota de Get /api/programas-pdde/{uuid}/",
    () => {
      it("Validar Get no endpoint /api/programas-pdde/{uuid}/ com sucesso", () => {
        var id = "";
        cy.validar_programas_pdde(id).then((response) => {
          expect(response.status).to.eq(200);
          id = response.body.results[0].uuid;
          cy.validar_programas_pdde(id).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body.uuid).to.eq(id);
            expect(response.body.id).to.exist;
            expect(response.body.nome).to.exist;
          });
        });
      });

      it("Validar Get no endpoint /api/programas-pdde/{uuid}/ com uuid invalido", () => {
        var id = "fd4";
        cy.validar_programas_pdde(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });
    }
  );

  context("Casos de teste para a rota de Post /api/programas-pdde/", () => {
    it("Validar Post no endpoint /api/programas-pdde/ com sucesso", () => {
      var body = { nome: "Teste automatizado " + new Date().getTime() };
      cy.cadastrar_programas_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body.nome).to.eq(body.nome);
        expect(response.body.id).to.exist;
        expect(response.body.uuid).to.exist;
        var id = response.body.uuid;
        cy.excluir_programas_pdde(id).then((responseExcluir) => {
          expect(responseExcluir.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint /api/programas-pdde/ com nome duplicado", () => {
      var body = { nome: "Teste automatizado " + new Date().getTime() };
      cy.cadastrar_programas_pdde(body).then((responseCadastro) => {
        expect(responseCadastro.status).to.eq(201);
        var id = responseCadastro.body.uuid;
        cy.cadastrar_programas_pdde(body).then((response) => {
          expect(response.status).to.eq(400);
          expect(response.body.detail).to.eq(
            "Erro ao criar Programa PDDE. Já existe um Programa PDDE cadastrado com este nome."
          );
          expect(response.body.erro).to.eq("Duplicated");
        });
        cy.excluir_programas_pdde(id).then((responseExcluir) => {
          expect(responseExcluir.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint /api/programas-pdde/ com nome em branco", () => {
      var body = { nome: "" };
      cy.cadastrar_programas_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.nome).to.eq(
          "Nome do Programa PDDE não foi informado."
        );
      });
    });
  });

  context(
    "Casos de teste para a rota de Delete /api/programas-pdde/{uuid}/",
    () => {
      it("Validar Delete no endpoint /api/programas-pdde/{uuid}/ com sucesso", () => {
        var body = { nome: "Teste automatizado " + new Date().getTime() };
        cy.cadastrar_programas_pdde(body).then((responseCadastro) => {
          expect(responseCadastro.status).to.eq(201);
          var id = responseCadastro.body.uuid;
          cy.excluir_programas_pdde(id).then((response) => {
            expect(response.status).to.eq(204);
          });
        });
      });

      it("Validar Delete no endpoint /api/programas-pdde/{uuid}/ com uuid invalido", () => {
        var id = "responseCadastro.body.uuid";
        cy.excluir_programas_pdde(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });

      it("Validar Delete no endpoint /api/programas-pdde/{uuid}/ com uuid em branco", () => {
        var id = "";
        cy.excluir_programas_pdde(id).then((response) => {
          expect(response.status).to.eq(405);
          expect(response.statusText).to.eq("Method Not Allowed");
          expect(response.body.detail).to.eq('Method "DELETE" not allowed.');
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Put /api/programas-pdde/{uuid}/",
    () => {
      it("Validar Put no endpoint /api/programas-pdde/{uuid}/ com sucesso", () => {
        var body = { nome: "Teste automatizado " + new Date().getTime() };
        cy.cadastrar_programas_pdde(body).then((response) => {
          expect(response.status).to.eq(201);
          var id = response.body.uuid;
          body = { nome: "teste automatizado editado" };
          cy.alterar_programas_pdde(body, id).then((responseAlterar) => {
            expect(responseAlterar.status).to.eq(200);
            expect(responseAlterar.body.nome).to.eq(body.nome);
            expect(responseAlterar.body.id).to.exist;
            expect(responseAlterar.body.uuid).to.exist;
            cy.excluir_programas_pdde(id).then((responseExcluir) => {
              expect(responseExcluir.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint /api/programas-pdde/{uuid}/ com nome em branco", () => {
        var body = { nome: "Teste automatizado " + new Date().getTime() };
        cy.cadastrar_programas_pdde(body).then((response) => {
          expect(response.status).to.eq(201);
          var id = response.body.uuid;
          body = { nome: "" };
          cy.alterar_programas_pdde(body, id).then((responseAlterar) => {
            expect(responseAlterar.status).to.eq(400);
            expect(responseAlterar.body.nome[0]).to.eq(
              "This field may not be blank."
            );
            cy.excluir_programas_pdde(id).then((responseExcluir) => {
              expect(responseExcluir.status).to.eq(204);
            });
          });
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Patch /api/programas-pdde/{uuid}/",
    () => {
      it("Validar Patch no endpoint /api/programas-pdde/{uuid}/ com sucesso", () => {
        var body = { nome: "Teste automatizado " + new Date().getTime() };
        cy.cadastrar_programas_pdde(body).then((response) => {
          expect(response.status).to.eq(201);
          var id = response.body.uuid;
          body = { nome: "teste automatizado editado" };
          cy.editar_programas_pdde(body, id).then((responseAlterar) => {
            expect(responseAlterar.status).to.eq(200);
            expect(responseAlterar.body.nome).to.eq(body.nome);
            expect(responseAlterar.body.id).to.exist;
            expect(responseAlterar.body.uuid).to.exist;
            cy.excluir_programas_pdde(id).then((responseExcluir) => {
              expect(responseExcluir.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint /api/programas-pdde/{uuid}/ com nome em branco", () => {
        var body = { nome: "Teste automatizado " + new Date().getTime() };
        cy.cadastrar_programas_pdde(body).then((response) => {
          expect(response.status).to.eq(201);
          var id = response.body.uuid;
          body = { nome: "" };
          cy.editar_programas_pdde(body, id).then((responseAlterar) => {
            expect(responseAlterar.status).to.eq(400);
            expect(responseAlterar.body.nome[0]).to.eq(
              "This field may not be blank."
            );
            cy.excluir_programas_pdde(id).then((responseExcluir) => {
              expect(responseExcluir.status).to.eq(204);
            });
          });
        });
      });
    }
  );
});
