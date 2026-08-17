import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given(
  "crio o Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    cy.criar_motivo_pagamento_antecipado(motivo);
  },
);

Then(
  "excluo o Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    cy.excluir_motivo_pagamento_antecipado_por_nome(motivo);
  },
);
