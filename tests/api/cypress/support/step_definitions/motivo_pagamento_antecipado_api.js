import { Given, Then } from "cypress-cucumber-preprocessor/steps";

Given(
  "crio o Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    return cy.criar_motivo_pagamento_antecipado(motivo);
  },
);

Then(
  "excluo o Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    return cy.excluir_motivo_pagamento_antecipado_por_nome(motivo);
  },
);

Then(
  "excluo e confirmo o Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    return cy.excluir_motivo_pagamento_antecipado_por_nome(motivo, {
      exigirExistencia: true,
    });
  },
);

Then(
  "confirmo que o Motivo pagamento antecipado com o nome de motivo {string} não existe via API",
  (motivo) => {
    return cy.confirmar_motivo_pagamento_antecipado_ausente(motivo);
  },
);

Then(
  "confirmo que existe exatamente um Motivo pagamento antecipado com o nome de motivo {string} via API",
  (motivo) => {
    return cy.confirmar_motivo_pagamento_antecipado_existente(motivo);
  },
);
