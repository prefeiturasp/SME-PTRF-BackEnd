/// <reference types='cypress' />

describe('Validar rotas de login da aplicação SigEscola', () => {

	context('Casos de teste para a rota api/login/', () => {

		it('Validar login realizado com sucesso', () => {
			var usuario = Cypress.config('usuario_homol_sme')
			var senha = Cypress.config('senha_homol')

			cy.autenticar_login(usuario, senha).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.statusText).to.eq('OK')
				expect(response.allRequestResponses[0]['Response Body'].access).to.exist
			})
		})

		it('Validar login com senha invalida', () => {
			var usuario = Cypress.config('usuario_homol_sme')
			var senha = 'senha_invalida'

			cy.autenticar_login(usuario, senha).then((response) => {
				expect(response.status).to.eq(401)
				expect(response.statusText).to.eq('Unauthorized')
			})
		})

		it('Validar login com usuario em branco', () => {
			var usuario = ''
			var senha = Cypress.config('senha_homol')

			cy.autenticar_login(usuario, senha).then((response) => {
				expect(response.status).to.eq(400)
			})
		})

		it('Validar login com senha em branco', () => {
			var usuario = Cypress.config('usuario_homol_sme')
			var senha = ''

			cy.autenticar_login(usuario, senha).then((response) => {
				expect(response.status).to.eq(400)
			})
		})

		it('Validar login sem informar usuario e senha', () => {
			var usuario = ''
			var senha = ''

			cy.autenticar_login(usuario, senha).then((response) => {
				expect(response.status).to.eq(400)
			})
		})

	})

})
