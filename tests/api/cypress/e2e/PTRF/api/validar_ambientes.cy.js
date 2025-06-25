/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get api/ambientes/', () => {
		it('Validar Get no endpoint api/ambientes/ com sucesso', () => {
			var id = ''
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get api/ambientes/{id}/', () => {
		it('Validar Get no endpoint api/ambientes/{id}/ com sucesso', () => {
			var id = ''
			cy.validar_ambiente(id).then((responseId) => {
				id = responseId.body[0].id
				cy.validar_ambiente(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.id).to.eq(1)
					expect(response.body.nome).to.exist
					expect(response.body.prefixo).to.exist
				})
			})

		})

		it('Validar Get no endpoint api/ambientes/{id}/ com id invalido', () => {
			var id = 'teste'
				cy.validar_ambiente(id).then((response) => {
					expect(response.status).to.eq(404)
					expect(response.statusText).to.eq('Not Found')
			})

		})

	})
})

