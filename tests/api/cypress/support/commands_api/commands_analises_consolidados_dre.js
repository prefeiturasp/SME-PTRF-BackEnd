/// <reference types='cypress' />

Cypress.Commands.add('validar_analises_consolidados_dre', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/analises-consolidados-dre/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_download_documento_pdf_devolucao_acertos_dre', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/analises-consolidados-dre/download-documento-pdf_devolucao_acertos/?analise_consolidado_uuid=${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_previa_relatorio_devolucao_acertos_dre', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/analises-consolidados-dre/previa-relatorio-devolucao-acertos/?analise_consolidado_uuid=${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_status_info_relatorio_devolucao_acertos_dre', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/analises-consolidados-dre/status-info_relatorio_devolucao_acertos/?analise_consolidado_uuid=${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

