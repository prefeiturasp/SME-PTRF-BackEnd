/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')

	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	// =========================
	// GET /api/composicoes/
	// =========================
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

		it('Validar Get no endpoint /api/composicoes/ retornando lista', () => {
			cy.validar_composicoes('').then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.results).to.be.an('array')
			})
		})

		it('Validar que a lista possui ao menos um registro', () => {
			cy.validar_composicoes('').then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.results.length).to.be.greaterThan(0)
			})
		})

		it('Validar estrutura basica dos itens da lista', () => {
			cy.validar_composicoes('').then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.results[0]).to.have.property('uuid')
				expect(response.body.results[0]).to.have.property('id')
				expect(response.body.results[0]).to.have.property('associacao')
			})
		})

	})

	// =========================
	// GET /api/composicoes/{uuid}/
	// =========================
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
			cy.validar_composicoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Get no endpoint /api/composicoes/{uuid}/ com uuid inexistente', () => {
			var id = '11111111-1111-1111-1111-111111111111'
			cy.validar_composicoes(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint /api/composicoes/{uuid}/ com uuid em branco', () => {
			var id = ''
			cy.validar_composicoes(id).then((response) => {
				expect(response.status).to.eq(200)
			})
		})

	})

})