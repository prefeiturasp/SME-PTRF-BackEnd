/// <reference types='cypress' />

import massa from "../../../../fixtures/valores_reprogramados.json";

describe(
  "Validar listagem de valores reprogramados por DRE",
  {
    retries: 0,
    env: { allureAttachRequests: false },
  },
  () => {
    var usuario = Cypress.config("usuario_homol_dre");
    var senha = Cypress.config("senha_homol");
    var lista = [];
    var unidades = [];
    var status_validos = [];
    var headers;

    before(() => {
      expect(Boolean(usuario), "USUARIO_HOMOL_DRE configurado").to.eq(true);
      expect(Boolean(senha), "SENHA_HOMOL configurada").to.eq(true);
      cy.autenticar_login(usuario, senha);
      cy.then(() => {
        expect(globalThis.token, "login DRE forneceu token").to.be.a("string")
          .and.not.be.empty;
        headers = {
          Authorization: "JWT " + globalThis.token,
          "X-Recurso-Selecionado": massa.recurso_uuid,
        };
      });
      cy.then(() =>
        cy.request({
          url: Cypress.config("baseUrlPTRFHomol") + "api/unidades/",
          headers,
          qs: { dre__uuid: massa.dre_uuid },
          timeout: 120000,
        }),
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.be.an("array");
        unidades = response.body;
      });
      cy.then(() =>
        cy.request({
          url:
            Cypress.config("baseUrlPTRFHomol") +
            "api/valores-reprogramados/tabelas/",
          headers,
        }),
      ).then((response) => {
        expect(response.status).to.eq(200);
        status_validos = response.body.status.map((status) => status.id);
      });
      // Referência sem filtros para comprovar que os controles eram elegíveis.
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.be.an("array");
        lista = response.body;
      });
    });

    // Reutilizado nos cenários: massa ausente deve falhar com uma mensagem explícita.
    function validar_massa(registro) {
      var item = lista.find((item) => item.associacao.uuid === registro.uuid);
      var unidade = unidades.find(
        (item) => item.uuid === registro.unidade_uuid,
      );
      expect(item, "associação elegível: " + registro.uuid).to.exist;
      expect(unidade, "cadastro da unidade: " + registro.unidade_uuid).to.exist;
      expect(item.associacao.nome).to.eq(registro.nome);
      expect(item.associacao.unidade.uuid).to.eq(registro.unidade_uuid);
      expect(unidade.nome).to.eq(registro.unidade_nome);
      expect(unidade.codigo_eol).to.eq(registro.codigo_eol);
      expect(unidade.tipo_unidade).to.eq(registro.tipo_unidade);
      expect(unidade.nome_dre).to.eq(massa.dre_nome);
      return item;
    }

    it("CT01 - Listar por DRE sem filtros opcionais", () => {
      validar_massa(massa.mary);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.headers["content-type"]).to.include("application/json");
        expect(response.body).to.be.an("array");
        expect(response.body.map((item) => item.associacao.uuid)).to.include(
          massa.mary.uuid,
        );
        response.body.forEach((item) => {
          var unidade = unidades.find(
            (unidade) => unidade.uuid === item.associacao.unidade.uuid,
          );
          expect(unidade, "unidade pertence ao cadastro da DRE").to.exist;
          expect(unidade.nome_dre).to.eq(massa.dre_nome);
          expect(item.associacao.unidade.nome_dre).to.eq(massa.dre_nome);
        });
      });
    });

    it("CT03 - Buscar por parte exclusiva do nome da associação", () => {
      validar_massa(massa.gomes);
      validar_massa(massa.mary);
      var search = "apmescola";
      expect(massa.gomes.nome.toLowerCase()).to.include(search);
      expect(massa.gomes.unidade_nome.toLowerCase()).not.to.include(search);
      expect(massa.gomes.codigo_eol).not.to.include(search);
      expect(
        (
          massa.mary.nome +
          massa.mary.unidade_nome +
          massa.mary.codigo_eol
        ).toLowerCase(),
      ).not.to.include(search);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, search },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        var associados = response.body.map((item) => item.associacao.uuid);
        expect(associados).to.include(massa.gomes.uuid);
        expect(associados).not.to.include(massa.mary.uuid);
      });
    });

    it("CT04 - Buscar por parte exclusiva do nome da unidade em minúsculas", () => {
      validar_massa(massa.rodrigo);
      validar_massa(massa.mary);
      // Cadastro de QA consultado sem nomes acentuados; JUNIOR consta como JR na associação.
      var search = "junior";
      expect(massa.rodrigo.unidade_nome.toLowerCase()).to.include(search);
      expect(massa.rodrigo.nome.toLowerCase()).not.to.include(search);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, search },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.map((item) => item.associacao.uuid)).to.include(
          massa.rodrigo.uuid,
        );
        expect(
          response.body.map((item) => item.associacao.uuid),
        ).not.to.include(massa.mary.uuid);
      });
    });

    it("CT05 - Buscar pelo Código EOL completo preservando zeros à esquerda", () => {
      validar_massa(massa.assad);
      validar_massa(massa.mary);
      var search = massa.assad.codigo_eol;
      expect(search).to.eq("000485");
      lista.forEach((item) => {
        expect(item.associacao.nome).not.to.include(search);
        expect(item.associacao.unidade.nome_com_tipo).not.to.include(search);
      });
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, search },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.map((item) => item.associacao.uuid)).to.include(
          massa.assad.uuid,
        );
        response.body.forEach((item) =>
          expect(item.associacao.unidade.codigo_eol).to.eq(search),
        );
      });
    });

    it("CT06 - Consultar um termo sem correspondência", () => {
      var search = "qa_sem_correspondencia_" + Date.now();
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, search },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.deep.eq([]);
      });
    });

    it("CT07 - Filtrar por tipo de unidade e excluir outro tipo", () => {
      validar_massa(massa.mary);
      validar_massa(massa.assad);
      expect(massa.mary.tipo_unidade).not.to.eq(massa.assad.tipo_unidade);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, tipo_unidade: massa.mary.tipo_unidade },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.map((item) => item.associacao.uuid)).to.include(
          massa.mary.uuid,
        );
        expect(
          response.body.map((item) => item.associacao.uuid),
        ).not.to.include(massa.assad.uuid);
        response.body.forEach((item) => {
          var unidade = unidades.find(
            (unidade) => unidade.uuid === item.associacao.unidade.uuid,
          );
          expect(unidade, "unidade no cadastro de referência").to.exist;
          expect(unidade.tipo_unidade).to.eq(massa.mary.tipo_unidade);
        });
      });
    });

    it("CT08 - Filtrar por um status válido para o recurso", () => {
      expect(
        validar_massa(massa.mary).associacao.status_valores_reprogramados,
      ).to.eq(massa.mary.status);
      expect(
        validar_massa(massa.gomes).associacao.status_valores_reprogramados,
      ).to.eq(massa.gomes.status);
      expect(status_validos).to.include(massa.mary.status);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, status: massa.mary.status },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.map((item) => item.associacao.uuid)).to.include(
          massa.mary.uuid,
        );
        expect(
          response.body.map((item) => item.associacao.uuid),
        ).not.to.include(massa.gomes.uuid);
        response.body.forEach((item) =>
          expect(item.associacao.status_valores_reprogramados).to.eq(
            massa.mary.status,
          ),
        );
      });
    });

    it("CT09 - Filtrar por dois status separados por vírgula", () => {
      expect(
        validar_massa(massa.mary).associacao.status_valores_reprogramados,
      ).to.eq(massa.mary.status);
      expect(
        validar_massa(massa.gomes).associacao.status_valores_reprogramados,
      ).to.eq(massa.gomes.status);
      expect(
        validar_massa(massa.manoel).associacao.status_valores_reprogramados,
      ).to.eq(massa.manoel.status);
      var status = [massa.mary.status, massa.gomes.status];
      expect(status_validos).to.include.members(status);
      expect(status[0]).not.to.eq(status[1]);
      cy.validar_valores_reprogramados(
        { dre_uuid: massa.dre_uuid, status: status.join(",") },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        var associados = response.body.map((item) => item.associacao.uuid);
        expect(associados).to.include(massa.mary.uuid);
        expect(
          associados,
          "segundo status também deve ser considerado",
        ).to.include(massa.gomes.uuid);
        expect(associados).not.to.include(massa.manoel.uuid);
        response.body.forEach((item) =>
          expect(status).to.include(
            item.associacao.status_valores_reprogramados,
          ),
        );
      });
    });

    it("CT10 - Combinar busca, tipo de unidade e status", () => {
      // Um controle para cada filtro: Leila (busca), Assad (tipo), Gomes (status).
      var search = "APM";
      var registros = [massa.mary, massa.assad, massa.gomes, massa.leila];
      registros.forEach((registro) => {
        expect(
          validar_massa(registro).associacao.status_valores_reprogramados,
        ).to.eq(registro.status);
      });
      expect(massa.mary.nome).to.include(search);
      expect(massa.assad.nome).to.include(search);
      expect(massa.gomes.nome).to.include(search);
      expect(massa.leila.nome + massa.leila.unidade_nome).not.to.include(
        search,
      );
      expect(massa.assad.tipo_unidade).not.to.eq(massa.mary.tipo_unidade);
      expect(massa.assad.status).to.eq(massa.mary.status);
      expect(massa.gomes.tipo_unidade).to.eq(massa.mary.tipo_unidade);
      expect(massa.gomes.status).not.to.eq(massa.mary.status);
      expect(massa.leila.tipo_unidade).to.eq(massa.mary.tipo_unidade);
      expect(massa.leila.status).to.eq(massa.mary.status);
      cy.validar_valores_reprogramados(
        {
          dre_uuid: massa.dre_uuid,
          search,
          tipo_unidade: massa.mary.tipo_unidade,
          status: massa.mary.status,
        },
        massa.recurso_uuid,
      ).then((response) => {
        expect(response.status).to.eq(200);
        var associados = response.body.map((item) => item.associacao.uuid);
        expect(associados).to.include(massa.mary.uuid);
        expect(associados).not.to.include(massa.assad.uuid);
        expect(associados).not.to.include(massa.gomes.uuid);
        expect(associados).not.to.include(massa.leila.uuid);
      });
    });
  },
);
