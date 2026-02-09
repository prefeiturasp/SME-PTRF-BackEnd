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

		it('Validar estrutura do retorno no endpoint api/ambientes/', () => {
			var id = ''
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.be.an('array')
				if (response.body.length > 0) {
					expect(response.body[0]).to.have.property('id')
					expect(response.body[0]).to.have.property('nome')
					expect(response.body[0]).to.have.property('prefixo')
				}
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
					expect(response.body.id).to.eq(id)
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

		it('Validar Get no endpoint api/ambientes/{id}/ com id negativo', () => {
			var id = -1
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ambientes/{id}/ com id zero', () => {
			var id = 0
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ambientes/{id}/ com id decimal', () => {
			var id = 1.5
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ambientes/{id}/ com id válido porém inexistente', () => {
			var id = 999999
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ambientes/{id}/ com id em branco', () => {
			var id = ''
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

		it('Validar Get no endpoint api/ambientes/{id}/ com caracteres especiais', () => {
			var id = '@@@'
			cy.validar_ambiente(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

	})

})