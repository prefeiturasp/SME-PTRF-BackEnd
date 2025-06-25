import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('clico no botao {string} da tela Motivo pagamento antecipado', function (btn_motivo_pagamento_antecipado) {
	cy.clicar_btn_motivo_pagamento_antecipado(btn_motivo_pagamento_antecipado)
});

Dado('informo dado nos campos {string} da tela Motivo pagamento antecipado', function (nome_do_motivo_pagamento_antecipado) {
	cy.informar_dados_motivo_pagamento_antecipado(nome_do_motivo_pagamento_antecipado)
});

Dado('informo dado nos campos {string} da tela de pesquisa de Motivo pagamento antecipado', function (nome_do_motivo_pagamento_antecipado) {
	cy.informar_dados_pesquisa_motivo_pagamento_antecipado(nome_do_motivo_pagamento_antecipado)
});

