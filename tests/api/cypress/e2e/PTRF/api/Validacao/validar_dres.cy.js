/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')

	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	// =========================
	// GET /api/dres/
	// =========================
	context('Casos de teste para a rota de Get /api/dres/', () => {

		it('Validar Get no endpoint /api/dres/ com sucesso', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

		it('Validar Get no endpoint /api/dres/ retornando lista', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.be.an('array')
			})
		})

		it('Validar que a lista de dres não está vazia', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.length).to.be.greaterThan(0)
			})
		})

		it('Validar estrutura basica do primeiro item da lista', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body[0]).to.have.property('uuid')
				expect(response.body[0]).to.have.property('dre')
			})
		})

	})

	// =========================
	// GET /api/dres/{uuid}/
	// =========================
	context('Casos de teste para a rota de Get /api/dres/{uuid}/', () => {

		it('Validar Get no endpoint /api/dres/{uuid}/ com sucesso', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				var id = response.body[0].uuid
				cy.validar_dres_id(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.dre).to.exist
					expect(response.body).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/dres/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_dres_id(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Get no endpoint /api/dres/{uuid}/ com uuid inexistente', () => {
			var id = '11111111-1111-1111-1111-111111111111'
			cy.validar_dres_id(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

	})

	// =========================
	// GET /api/dres/{uuid}/qtd-unidades/
	// =========================
	context('Casos de teste para a rota de Get /api/dres/{uuid}/qtd-unidades/', () => {

		it('Validar Get no endpoint /api/dres/{uuid}/qtd-unidades/ com sucesso', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				var id = response.body[0].uuid
				cy.validar_dres_qtd_unidades(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.qtd_unidades).to.exist
					expect(response.body).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/dres/{uuid}/qtd-unidades/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_dres_qtd_unidades(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Get no endpoint /api/dres/{uuid}/qtd-unidades/ com uuid inexistente', () => {
			var id = '11111111-1111-1111-1111-111111111111'
			cy.validar_dres_qtd_unidades(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

	})

})