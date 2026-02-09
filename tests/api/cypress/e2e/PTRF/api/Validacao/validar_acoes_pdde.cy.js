/// <reference types='cypress' />

describe("Validar rotas de acoes da aplicação SigEscola", () => {
  var usuario = Cypress.config("usuario_homol_sme");
  var senha = Cypress.config("senha_homol");
  before(() => {
    cy.autenticar_login(usuario, senha);
  });

  context("Casos de teste para a rota de Get /api/acoes-pdde/", () => {
    it("Validar Get no endpoint /api/acoes-pdde/ com sucesso sem parametros", () => {
      var id = "";
      cy.validar_acoes_pdde(id).then((response) => {
        cy.log(JSON.stringify(response.body));
        console.log(response);
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });

    it("Validar Get no endpoint /api/acoes-pdde/ com sucesso e com todos parametros preenchidos paramentros", () => {
      var id =
        "?aceita_capital=true&aceita_custeio=false&aceita_livre_aplicacao=true&page=1&page_size=10";
      cy.validar_acoes_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });

    it("Validar Get no endpoint /api/acoes-pdde/ com sucesso e com paramentros de page e page size preenchidos", () => {
      var id = "?page=1&page_size=10";
      cy.validar_acoes_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.results).to.exist;
        expect(response.body.page).to.eq(1);
        expect(response.body.page_size).to.eq(10);
        expect(response.body.links).to.exist;
      });
    });
  });

  context("Casos de teste para a rota de Get /api/acoes-pdde/{uuid}/", () => {
    it("Validar Get no endpoint /api/acoes-pdde/{uuid}/ com sucesso", () => {
      var id = "";
      cy.validar_acoes_pdde(id).then((response) => {
        expect(response.status).to.eq(200);
        id = response.body.results[0].uuid;
        cy.validar_acoes_pdde(id).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body.uuid).to.eq(id);
          expect(response.body.id).to.exist;
          expect(response.body.nome).to.exist;
          expect(response.body.aceita_capital).to.exist;
          expect(response.body.aceita_custeio).to.exist;
          expect(response.body.aceita_livre_aplicacao).to.exist;
          expect(response.body.programa_objeto).to.exist;
        });
      });
    });

    it("Validar Get no endpoint /api/acoes-pdde/{uuid}/ com uuid invalido", () => {
      var id = "fd4";
      cy.validar_acoes_pdde(id).then((response) => {
        expect(response.status).to.eq(404);
        expect(response.statusText).to.eq("Not Found");
      });
    });
  });

  context("Casos de teste para a rota de Post /api/acoes-pdde/", () => {
    it("Validar Post no endpoint /api/acoes-pdde/ com sucesso", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body.nome).to.eq(body.nome);
        expect(response.body.aceita_capital).to.eq(body.aceita_capital);
        expect(response.body.aceita_custeio).to.eq(body.aceita_custeio);
        expect(response.body.aceita_livre_aplicacao).to.eq(
          body.aceita_livre_aplicacao
        );
        expect(response.body.programa).to.eq(body.programa);
        expect(response.body.id).to.exist;
        expect(response.body.uuid).to.exist;
        var id = response.body.uuid;
        cy.excluir_acoes_pdde(id).then((responseExcluir) => {
          expect(responseExcluir.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com nome duplicado", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((responseCadastro) => {
        expect(responseCadastro.status).to.eq(201);
        var id = responseCadastro.body.uuid;
        cy.cadastrar_acoes_pdde(body).then((response) => {
          expect(response.status).to.eq(400);
          expect(response.body.detail).to.eq(
            "Erro ao criar Ação PDDE. Já existe uma Ação PDDE cadastrada com este nome e programa."
          );
          expect(response.body.erro).to.eq("Duplicated");
        });
        cy.excluir_acoes_pdde(id).then((responseExcluir) => {
          expect(responseExcluir.status).to.eq(204);
        });
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com nome em branco", () => {
      var body = {
        nome: "",
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.nome).to.eq(
          "Nome da ação PDDE não foi informado."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ nome com mais de 160 posicoes", () => {
      var body = {
        nome: "asdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklç1",
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.nome[0]).to.eq(
          "Ensure this field has no more than 160 characters."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com programa zerada", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: 0,
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.programa).to.eq(
          "O Programa PDDE não foi informado."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com programa em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.programa).to.eq(
          "O Programa PDDE não foi informado."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com programa null", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: null,
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.programa).to.eq(
          "O Programa PDDE não foi informado."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita capital com valor invalido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: "fa",
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_capital[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita capital com valor em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: "",
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_capital[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita custeio com valor em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: "",
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_custeio[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita custeio com valor invalido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: "fal",
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_custeio[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita custeio com valor invalido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: "fal",
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_livre_aplicacao[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });

    it("Validar Post no endpoint /api/acoes-pdde/ com aceita custeio com valor em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: "",
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(400);
        expect(response.body.aceita_livre_aplicacao[0]).to.eq(
          "Must be a valid boolean."
        );
      });
    });
  });

  context(
    "Casos de teste para a rota de Delete /api/acoes-pdde/{uuid}/",
    () => {
      it("Validar Delete no endpoint /api/acoes-pdde/{uuid}/ com sucesso", () => {
        var body = {
          nome: "teste automatizado " + new Date().getTime(),
          programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.cadastrar_acoes_pdde(body).then((responseCadastro) => {
          expect(responseCadastro.status).to.eq(201);
          var id = responseCadastro.body.uuid;
          cy.excluir_acoes_pdde(id).then((response) => {
            expect(response.status).to.eq(204);
          });
        });
      });

      it("Validar Delete no endpoint /api/acoes-pdde/{uuid}/ com uuid invalido", () => {
        var id = "responseCadastro.body.uuid";
        cy.excluir_acoes_pdde(id).then((response) => {
          expect(response.status).to.eq(404);
          expect(response.statusText).to.eq("Not Found");
        });
      });

      it("Validar Delete no endpoint /api/acoes-pdde/{uuid}/ com uuid em branco", () => {
        var id = "";
        cy.excluir_acoes_pdde(id).then((response) => {
          expect(response.status).to.eq(405);
          expect(response.statusText).to.eq("Method Not Allowed");
          expect(response.body.detail).to.eq('Method "DELETE" not allowed.');
        });
      });
    }
  );

  context("Casos de teste para a rota de Put /api/acoes-pdde/{uuid}/", () => {
    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com sucesso", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(200);
          expect(responseAlterar.body.nome).to.eq(body.nome);
          expect(responseAlterar.body.aceita_capital).to.eq(
            body.aceita_capital
          );
          expect(responseAlterar.body.aceita_custeio).to.eq(
            body.aceita_custeio
          );
          expect(responseAlterar.body.aceita_livre_aplicacao).to.eq(
            body.aceita_livre_aplicacao
          );
          expect(responseAlterar.body.programa).to.eq(body.programa);
          expect(responseAlterar.body.id).to.exist;
          expect(responseAlterar.body.uuid).to.exist;
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com nome em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "",
          programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.nome).to.eq(
            "Nome da ação PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com nome com mais de 160 posições", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "asdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklç1",
          programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.nome[0]).to.eq(
            "Ensure this field has no more than 160 characters."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com programa em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: null,
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.programa).to.eq(
            "O Programa PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com programa zerada", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: 0,
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.programa).to.eq(
            "O Programa PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita capital em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: "",
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_capital[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita capital inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: "fa",
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_capital[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita custeio inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: "te",
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_custeio[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita custeio em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: "",
          aceita_livre_aplicacao: true,
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_custeio[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita livre aplicacao inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: "tr",
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_livre_aplicacao[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Put no endpoint /api/acoes-pdde/{uuid}/ com aceita livre aplicacao em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: "",
        };
        cy.alterar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_livre_aplicacao[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });
  });

  context("Casos de teste para a rota de Patch /api/acoes-pdde/{uuid}/", () => {
    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com sucesso", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(200);
          expect(responseAlterar.body.nome).to.eq(body.nome);
          expect(responseAlterar.body.aceita_capital).to.eq(
            body.aceita_capital
          );
          expect(responseAlterar.body.aceita_custeio).to.eq(
            body.aceita_custeio
          );
          expect(responseAlterar.body.aceita_livre_aplicacao).to.eq(
            body.aceita_livre_aplicacao
          );
          expect(responseAlterar.body.programa).to.eq(body.programa);
          expect(responseAlterar.body.id).to.exist;
          expect(responseAlterar.body.uuid).to.exist;
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com nome em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "",
          programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.nome).to.eq(
            "Nome da ação PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com nome com mais de 160 posições", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "asdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklçasdfghjklç1",
          programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.nome[0]).to.eq(
            "Ensure this field has no more than 160 characters."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com programa em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: null,
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.programa).to.eq(
            "O Programa PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com programa zerada", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: 0,
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.programa).to.eq(
            "O Programa PDDE não foi informado."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita capital em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: "",
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_capital[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita capital inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: "fa",
          aceita_custeio: true,
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_capital[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita custeio inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: "te",
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_custeio[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita custeio em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: "",
          aceita_livre_aplicacao: true,
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_custeio[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita livre aplicacao inválido", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "e397fa11-71fe-44a5-9883-49e29a23e8e4",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: "tr",
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_livre_aplicacao[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });

    it("Validar Patch no endpoint /api/acoes-pdde/{uuid}/ com aceita livre aplicacao em branco", () => {
      var body = {
        nome: "teste automatizado " + new Date().getTime(),
        programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
        aceita_capital: true,
        aceita_custeio: true,
        aceita_livre_aplicacao: true,
      };
      cy.cadastrar_acoes_pdde(body).then((response) => {
        expect(response.status).to.eq(201);
        var id = response.body.uuid;
        body = {
          nome: "teste automatizado editado",
          programa: "ba6fd433-647f-4671-9d60-2bf368ee8883",
          aceita_capital: true,
          aceita_custeio: true,
          aceita_livre_aplicacao: "",
        };
        cy.editar_acoes_pdde(body, id).then((responseAlterar) => {
          expect(responseAlterar.status).to.eq(400);
          expect(responseAlterar.body.aceita_livre_aplicacao[0]).to.eq(
            "Must be a valid boolean."
          );
          cy.excluir_acoes_pdde(id).then((responseExcluir) => {
            expect(responseExcluir.status).to.eq(204);
          });
        });
      });
    });
  });
});
