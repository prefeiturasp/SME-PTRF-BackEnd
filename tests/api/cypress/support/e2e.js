import postgreSQL from "cypress-postgresql";
postgreSQL.loadDBCommands();

import "./commands";

import "./commands_db/commands_sql";

import "./commands_ui/commands_login";
import "./commands_ui/commands_painel_parametrizacao";
import "./commands_ui/commands_tipos_de_contas";
import "./commands_ui/commands_fornecedores";
import "./commands_ui/commands_motivo_pagamento_antecipado";
import "./commands_ui/commands_tipo_de_documento";
import "./commands_ui/commands_commons";
import "./commands_ui/commands_tipos_de_transacao";

import "./commands_api/commands_login";
import "./commands_api/commands_acoes";
import "./commands_api/commands_acoes_associacoes";
import "./commands_api/commands_ambientes";
import "./commands_api/commands_analises_consolidados_dre";
import "./commands_api/commands_anos_analise_regularidade";
import "./commands_api/commands_demonstrativo_financeiro";
import "./commands_api/commands_especificacoes_materiais_servicos";
import "./commands_api/commands_programas_pdde";
import "./commands_api/commands_acoes_pdde";
import "./commands_api/commands_comissoes";
import "./commands_api/commands_comentarios_de_analises";
import "./commands_api/commands_composicoes";
import "./commands_api/commands_contas_associacoes";
import "./commands_api/commands_dres";
import "./commands_api/commands_receitas_previstas_paa";
import "./commands_api/commands_faq_categorias";

import "@shelex/cypress-allure-plugin";

// Hide fetch/XHR requests
const app = window.top;
if (!app.document.head.querySelector("[data-hide-command-log-request]")) {
  const style = app.document.createElement("style");
  style.innerHTML =
    ".command-name-request, .command-name-xhr { display: none }";
  style.setAttribute("data-hide-command-log-request", "");

  app.document.head.appendChild(style);
}
