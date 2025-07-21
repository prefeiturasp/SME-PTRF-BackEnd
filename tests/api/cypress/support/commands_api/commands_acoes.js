/// <reference types='cypress' />

Cypress.Commands.add('validar_acoes', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_acoes_com_associacoes_nao_vinculadas', (id) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}/associacoes-nao-vinculadas/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('validar_acoes_com_associacoes_nao_vinculadas_por_nome', (id,nome) => {
	cy.request({
		method: 'GET',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}/associacoes-nao-vinculadas-por-nome/${nome}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('cadastrar_acoes', (body) => {
	cy.request({
		method: 'POST',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('excluir_acoes', (id) => {
	cy.request({
		method: 'DELETE',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('editar_acoes', (body,id) => {
	cy.request({
		method: 'PUT',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

Cypress.Commands.add('alterar_acoes', (body,id) => {
	cy.request({
		method: 'PATCH',
		url: Cypress.config('baseUrlPTRFHomol') + `api/acoes/${id}/`,
		headers: {
			Authorization: 'JWT ' + globalThis.token,
		},
		body: body,
		failOnStatusCode: false,
	})
})

