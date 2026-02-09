/// <reference types='cypress' />

describe("Validar rotas de acoes da aplicação SigEscola", () => {
  var usuario = Cypress.config("usuario_homol_dre");
  var senha = Cypress.config("senha_homol");

  before(() => {
    cy.autenticar_login(usuario, senha);
  });

  context(
    "Casos de teste para a rota de Get api/analises-consolidados-dre/",
    () => {

      it("Validar Get no endpoint api/analises-consolidados-dre/ com sucesso", () => {
        var id = "";
        cy.validar_analises_consolidados_dre(id).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.exist;
        });
      });

      it("Validar estrutura do retorno no endpoint api/analises-consolidados-dre/", () => {
        var id = "";
        cy.validar_analises_consolidados_dre(id).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.be.an("array");
          if (response.body.length > 0) {
            expect(response.body[0]).to.have.property("uuid");
            expect(response.body[0]).to.have.property("consolidado_dre");
          }
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Get api/analises-consolidados-dre/{uuid}/",
    () => {

      it("Validar Get no endpoint api/analises-consolidados-dre/{uuid}/ com sucesso", () => {
        var id = "";
        cy.validar_analises_consolidados_dre(id).then((responseId) => {
          id = responseId.body[0].uuid;
          cy.validar_analises_consolidados_dre(id).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body.consolidado_dre).to.exist;
            expect(
              response.body.analises_de_documentos_do_relatorio_consolidao_dre
            ).to.exist;
            expect(response.body.uuid).to.eq(id);
          });
        });
      });

      it("Validar Get no endpoint api/analises-consolidados-dre/{uuid}/ com uuid inválido", () => {
        var id = "15632";
        cy.validar_analises_consolidados_dre(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });

      it("Validar Get no endpoint api/analises-consolidados-dre/{uuid}/ com uuid válido inexistente", () => {
        var id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa";
        cy.validar_analises_consolidados_dre(id).then((response) => {
          expect(response.status).to.eq(404);
        });
      });

      it("Validar Get no endpoint api/analises-consolidados-dre/{uuid}/ com caracteres especiais", () => {
        var id = "@@@";
        cy.validar_analises_consolidados_dre(id).then((response) => {
          expect(response.status).to.eq(404);
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Get api/analises-consolidados-dre/download-documento-pdf_devolucao_acertos/",
    () => {

      it("Validar Get com uuid inválido", () => {
        var id = "25f1c5c3-0a8b-4aaf-937a-15feee";
        cy.validar_download_documento_pdf_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              `“${id}” is not a valid UUID.`
            );
          }
        );
      });

      it("Validar Get com uuid em branco", () => {
        var id = "";
        cy.validar_download_documento_pdf_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              "This field may not be blank."
            );
          }
        );
      });

      it("Validar Get com uuid válido inexistente", () => {
        var id = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb";
        cy.validar_download_documento_pdf_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
          }
        );
      });
    }
  );

  context(
    "Casos de teste para a rota de Get api/analises-consolidados-dre/previa-relatorio-devolucao-acertos/",
    () => {

      it("Validar Get com sucesso", () => {
        var id = "25f1c5c3-0a8b-4aaf-937a-15feeec91dae";
        cy.validar_previa_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(200);
            expect(response.body.mensagem).to.eq(
              "Arquivo na fila para processamento."
            );
          }
        );
      });

      it("Validar Get com uuid inválido", () => {
        var id = "25f1c5c3-0a8b-4aaf-937a-15feeec91";
        cy.validar_previa_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              `“${id}” is not a valid UUID.`
            );
          }
        );
      });

      it("Validar Get com uuid em branco", () => {
        var id = "";
        cy.validar_previa_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              "This field may not be blank."
            );
          }
        );
      });
    }
  );

  context(
    "Casos de teste para a rota de Get api/analises-consolidados-dre/status-info_relatorio_devolucao_acertos/",
    () => {

      it("Validar Get com sucesso", () => {
        var id = "25f1c5c3-0a8b-4aaf-937a-15feeec91dae";
        cy.validar_status_info_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(200);
            expect(response.body).to.eq("Relatório sendo gerado...");
          }
        );
      });

      it("Validar Get com uuid inválido", () => {
        var id = "25f1c5c3-0a8b-4aaf-937a-15feeec91";
        cy.validar_status_info_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              `“${id}” is not a valid UUID.`
            );
          }
        );
      });

      it("Validar Get com uuid em branco", () => {
        var id = "";
        cy.validar_status_info_relatorio_devolucao_acertos_dre(id).then(
          (response) => {
            expect(response.status).to.eq(400);
            expect(response.body.analise_consolidado_uuid[0]).to.eq(
              "This field may not be blank."
            );
          }
        );
      });
    }
  );
});