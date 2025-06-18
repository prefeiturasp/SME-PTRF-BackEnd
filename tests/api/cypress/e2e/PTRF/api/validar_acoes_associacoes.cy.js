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
        var id = response.body.uuid;
        expect(response.status).to.eq(201);
        expect(response.body.acao).to.eq(body.acao);
        expect(response.body.associacao).to.eq(body.associacao);
        expect(response.body.status).to.eq(body.status);
        expect(response.body.uuid).to.exist;
        cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
          expect(responseExclusao.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com associacao invalida", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1fg",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.associacao[0]).to.eq(
          `“${body.associacao}” is not a valid UUID.`
        );
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com acao invalida", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e5",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.acao[0]).to.eq(
          `“${body.acao}” is not a valid UUID.`
        );
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com acao em branco", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1fg",
        acao: "",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.acao[0]).to.eq("This field may not be null.");
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com associacao em branco", () => {
      var body = {
        associacao: "",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "ATIVA",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.associacao[0]).to.eq(
          `This field may not be null.`
        );
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com status em branco", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.status[0]).to.eq('"" is not a valid choice.');
      });
    });

    it("Validar Post no endpoint api/acoes-associacoes/ com status invalido", () => {
      var body = {
        associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
        acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        status: "dsd",
      };
      cy.cadastrar_acoes_associacoes(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.status[0]).to.eq(
          `"${body.status}" is not a valid choice.`
        );
      });
    });
  });

  context(
    "Casos de teste para a rota de delete api/acoes-associacoes/{uuid}/",
    () => {
      it("Validar delete no endpoint api/acoes-associacoes/uuid/ com sucesso", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          cy.excluir_acoes_associacoes(id).then((response) => {
            expect(response.status).to.eq(204);
            expect(response.statusText).to.eq("No Content");
          });
        });
      });

      it("Validar delete no endpoint api/acoes-associacoes/uuid/ com uuid invalido", () => {
        var id = "fdf";
        cy.excluir_acoes_associacoes(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });

      it("Validar delete no endpoint api/acoes-associacoes/uuid/ com uuid em branco", () => {
        var id = "";
        cy.excluir_acoes_associacoes(id).then((response) => {
          expect(response.status).to.eq(405);
          expect(response.statusText).to.eq("Method Not Allowed");
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Put api/acoes-associacoes/{uuid}/",
    () => {
      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com sucesso", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body.acao).to.eq(body_alteracao.acao);
            expect(response.body.associacao).to.eq(body_alteracao.associacao);
            expect(response.body.status).to.eq(body_alteracao.status);
            expect(response.body.uuid).to.exist;
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com associacao invalida", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1fg",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.associacao[0]).to.eq(
              `“${body_alteracao.associacao}” is not a valid UUID.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com acao invalida", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92ejan",
            status: "ATIVA",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.acao[0]).to.eq(
              `“${body_alteracao.acao}” is not a valid UUID.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com associacao em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.associacao[0]).to.eq(
              `This field may not be null.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com acao em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "",
            status: "ATIVA",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.acao[0]).to.eq(`This field may not be null.`);
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com Status em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.status[0]).to.eq('"" is not a valid choice.');
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Put no endpoint api/acoes-associacoes/{uuid}/ com Status invalido", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "dsaa",
          };
          cy.editar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.status[0]).to.eq(
              `"${body_alteracao.status}" is not a valid choice.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Patch api/acoes-associacoes/{uuid}/",
    () => {
      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com sucesso", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(200);
            expect(response.body.acao).to.eq(body_alteracao.acao);
            expect(response.body.associacao).to.eq(body_alteracao.associacao);
            expect(response.body.status).to.eq(body_alteracao.status);
            expect(response.body.uuid).to.exist;
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com associacao invalida", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1fg",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.associacao[0]).to.eq(
              `“${body_alteracao.associacao}” is not a valid UUID.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com acao invalida", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92ejan",
            status: "ATIVA",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.acao[0]).to.eq(
              `“${body_alteracao.acao}” is not a valid UUID.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com associacao em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "ATIVA",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.associacao[0]).to.eq(
              `This field may not be null.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com acao em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "",
            status: "ATIVA",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.acao[0]).to.eq(`This field may not be null.`);
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com Status em branco", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.status[0]).to.eq('"" is not a valid choice.');
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });

      it("Validar Patch no endpoint api/acoes-associacoes/{uuid}/ com Status invalido", () => {
        var body = {
          associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
          acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
          status: "ATIVA",
        };
        cy.cadastrar_acoes_associacoes(body).then((responseCadastro) => {
          var id = responseCadastro.body.uuid;
          expect(responseCadastro.status).to.eq(201);
          var body_alteracao = {
            associacao: "840d3087-6092-4b3f-a0c3-69ead4b1022a",
            acao: "f50c0cb2-1635-4b91-8413-cd419d92e578",
            status: "dsaa",
          };
          cy.alterar_acoes_associacoes(body_alteracao, id).then((response) => {
            expect(response.status).to.eq(400);
            expect(response.body.status[0]).to.eq(
              `"${body_alteracao.status}" is not a valid choice.`
            );
            cy.excluir_acoes_associacoes(id).then((responseExclusao) => {
              expect(responseExclusao.status).to.eq(204);
            });
          });
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Post api/acoes-associacoes/incluir-lote/",
    () => {
      it("Validar Post no endpoint api/acoes-associacoes/incluir-lote/ com sucesso", () => {
        var body = {
          associacoes_uuids: ["c83eedf6-3e85-4fd2-9798-62321e757b9f"],
          acao_uuid: "f50c0cb2-1635-4b91-8413-cd419d92e578",
        };
        cy.cadastrar_acoes_associacoes_incluir_lote(body).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.mensagem).to.eq(
            "Unidades vinculadas à ação com sucesso."
          );
        });
      });

      it("Validar Post no endpoint api/acoes-associacoes/incluir-lote/ com acao_uuid em branco", () => {
        var body = {
          associacoes_uuids: ["c83eedf6-3e85-4fd2-9798-62321e757b9f"],
          acao_uuid: "",
        };
        cy.cadastrar_acoes_associacoes_incluir_lote(body).then((response) => {
          expect(response.status).to.eq(400);
          expect(response.body.erro).to.eq("Falta de informações");
          expect(response.body.mensagem).to.eq(
            "É necessário enviar a acao_uuid e lista associacoes_uuids."
          );
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Post api/acoes-associacoes/excluir-lote/",
    () => {
      it("Validar Post no endpoint api/acoes-associacoes/excluir-lote/ com sucesso", () => {
        var body = {
          lista_uuids: ["f50c0cb2-1635-4b91-8413-cd419d92e578"],
        };
        cy.cadastrar_acoes_associacoes_excluir_lote(body).then((response) => {
          expect(response.status).to.eq(201);
        });
      });

      it("Validar Post no endpoint api/acoes-associacoes/excluir-lote/ com valor invalido", () => {
        var body = {
          lista_uuids: ["f50c0cb2-1635-4b91-8413-cd419d92e5"],
        };
        cy.cadastrar_acoes_associacoes_excluir_lote(body).then((response) => {
          expect(response.body.erro).to.eq(
            "problema_ao_excluir_acoes_associacoes"
          );
          expect(response.body.mensagem).to.eq(
            "badly formed hexadecimal UUID string"
          );
          expect(response.status).to.eq(400);
        });
      });

      it("Validar Post no endpoint api/acoes-associacoes/excluir-lote/ com valor em branco", () => {
        var body = {
          lista_uuids: [],
        };
        cy.cadastrar_acoes_associacoes_excluir_lote(body).then((response) => {
          expect(response.status).to.eq(400);
          expect(response.body.erro).to.eq("Falta de informações");
          expect(response.body.mensagem).to.eq(
            "É necessário enviar a lista de uuids a serem apagados (lista_uuids)."
          );
        });
      });
    }
  );

  context("Casos de teste para a rota de Get api/acoes-associacoes/", () => {
    it("Validar Get no endpoint api/acoes-associacoes/ com acao uuid valido e status inativo", () => {
      var id =
        "?acao__uuid=82a4bd9a-5884-4a43-9ae9-4fee0855f9b7&associacao__uuid=&status=INATIVA";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.exist;
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ com acao uuid valido e status ativo", () => {
      var id =
        "?acao__uuid=82a4bd9a-5884-4a43-9ae9-4fee0855f9b7&associacao__uuid=&status=ATIVA";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.exist;
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ com acao, associacao uuid valido e status ativo", () => {
      var id =
        "?acao__uuid=82a4bd9a-5884-4a43-9ae9-4fee0855f9b7&associacao__uuid=5aa26087-0163-4b7a-b621-8eb1452e909b&status=ATIVA";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results[0].acao.uuid).to.eq(
          "82a4bd9a-5884-4a43-9ae9-4fee0855f9b7"
        );
        expect(response.body.results[0].acao.aceita_capital).to.exist;
        expect(response.body.results[0].acao.aceita_custeio).to.exist;
        expect(response.body.results[0].acao.aceita_livre).to.exist;
        expect(response.body.results[0].acao.e_recursos_proprios).to.exist;
        expect(response.body.results[0].acao.id).to.exist;
        expect(response.body.results[0].acao.nome).to.exist;
        expect(response.body.results[0].acao.posicao_nas_pesquisas).to.exist;
        expect(response.body.results[0].associacao.cnpj).to.exist;
        expect(response.body.results[0].associacao.encerrada).to.exist;
        expect(response.body.results[0].associacao.nome).to.exist;
        expect(response.body.results[0].associacao.status_valores_reprogramados)
          .to.exist;
        expect(response.body.results[0].associacao.unidade.uuid).to.exist;
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ com acao, associacao uuid valido e status Inativo", () => {
      var id =
        "?acao__uuid=82a4bd9a-5884-4a43-9ae9-4fee0855f9b7&associacao__uuid=5aa26087-0163-4b7a-b621-8eb1452e909b&status=INATIVA";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.exist;
      });
    });

    it("Validar Get no endpoint api/acoes-associacoes/ com dados invalidos", () => {
      var id = "?acao__uuid=fdsfsd&associacao__uuid=fdsfs&status=fdsfs";
      cy.validar_acoes_associacoes(id).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.acao__uuid[0]).to.eq("Enter a valid UUID.");
        expect(response.body.associacao__uuid[0]).to.eq("Enter a valid UUID.");
        expect(response.body.status[0]).to.eq(
          "Select a valid choice. fdsfs is not one of the available choices."
        );
      });
    });
  });

  context(
    "Casos de teste para a rota de Get api/acoes-associacoes/uuid",
    () => {
      it("Validar Get no endpoint api/acoes-associacoes/uuid com sucesso", () => {
        var id = "f234e1d2-d894-4445-bdbd-e01fc4db2cea";
        cy.validar_acoes_associacoes(id).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body.acao.uuid).to.exist;
          expect(response.body.acao.aceita_capital).to.exist;
          expect(response.body.acao.aceita_custeio).to.exist;
          expect(response.body.acao.aceita_livre).to.exist;
          expect(response.body.acao.e_recursos_proprios).to.exist;
          expect(response.body.acao.id).to.exist;
          expect(response.body.acao.nome).to.exist;
          expect(response.body.acao.posicao_nas_pesquisas).to.exist;
          expect(response.body.associacao.cnpj).to.exist;
          expect(response.body.associacao.encerrada).to.exist;
          expect(response.body.associacao.nome).to.exist;
          expect(response.body.associacao.status_valores_reprogramados).to
            .exist;
          expect(response.body.associacao.unidade.uuid).to.exist;
        });
      });

      it("Validar Get no endpoint api/acoes-associacoes/uuid com uuid invalido", () => {
        var id = "f234e1d2-d894-4445-bdbd-e01fc4db2";
        cy.validar_acoes_associacoes(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });
    }
  );

  context(
    "Casos de teste para a rota de Get /api/acoes-associacoes/{uuid}/obter-saldo-atual/",
    () => {
      it("Validar Get no endpoint /api/acoes-associacoes/{uuid}/obter-saldo-atual/ com sucesso", () => {
        var id = "f234e1d2-d894-4445-bdbd-e01fc4db2cea";
        cy.validar_acoes_associacoes_obter_saldo_atual(id).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body.saldo_atual_capital).to.exist;
          expect(response.body.saldo_atual_custeio).to.exist;
          expect(response.body.saldo_atual_livre).to.exist;
          // expect(response.body.saldo_atual_total).to.exist
        });
      });

      it("Validar Get no endpoint /api/acoes-associacoes/{uuid}/obter-saldo-atual/ com uuid invalido", () => {
        var id = "f234e1d2-d894-4445-bdbd-e01fc4db2";
        cy.validar_acoes_associacoes_obter_saldo_atual(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });

      it("Validar Get no endpoint /api/acoes-associacoes/{uuid}/obter-saldo-atual/ com uuid em branco", () => {
        var id = "";
        cy.validar_acoes_associacoes_obter_saldo_atual(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });
    }
  );
});
