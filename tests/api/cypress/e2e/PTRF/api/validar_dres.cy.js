/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/dres/', () => {
		it('Validar Get no endpoint /api/dres/ com sucesso', () => {
			cy.validar_dres().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

	})

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
	})

	context('Casos de teste para a rota de Get /api/dres/{uuid}/qtd-unidades/', () => {
		it('Validar Get no endpoint /api/dres/{uuid}/qtd-unidades com sucesso/', () => {
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

	})

})