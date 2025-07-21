/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/composicoes/', () => {
		it('Validar Get no endpoint /api/composicoes/ com sucesso', () => {
			var id = ''
			cy.validar_composicoes(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.count).to.exist
				expect(response.body.links).to.exist
				expect(response.body.page).to.exist
				expect(response.body.page_size).to.exist
				expect(response.body.results).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get /api/composicoes/{uuid}/', () => {
		it('Validar Get no endpoint /api/composicoes/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_composicoes(id).then((response) => {
				expect(response.status).to.eq(200)
				id = response.body.results[0].uuid
				cy.validar_composicoes(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.associacao).to.exist
					expect(response.body.uuid).to.eq(id)
					expect(response.body.id).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/composicoes/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_comissoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

})