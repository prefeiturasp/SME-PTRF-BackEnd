/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/comissoes/', () => {
		it('Validar Get no endpoint /api/comissoes/ com sucesso sem parametros', () => {
			var id = ''
			cy.validar_comissoes(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get /api/comissoes/{uuid}/', () => {
		it('Validar Get no endpoint /api/comissoes/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_comissoes(id).then((response) => {
				expect(response.status).to.eq(200)
				id = response.body[0].uuid
				cy.validar_comissoes(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.id).to.exist
					expect(response.body.nome).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/comissoes/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_comissoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post /api/comissoes/', () => {
		it('Validar Post no endpoint /api/comissoes/ com sucesso', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.nome).to.eq(body.nome)
				expect(response.body.id).to.exist
				expect(response.body.uuid).to.exist
				var id = response.body.uuid
				cy.excluir_comissoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/comissoes/ com nome em branco', () => {
			var body = { nome: "" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.nome[0]).to.eq("This field may not be blank.")
			})
		})
	})

	context('Casos de teste para a rota de Delete /api/comissoes/{uuid}/', () => {
		it('Validar Delete no endpoint /api/comissoes/{uuid}/ com sucesso', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((responseCadastro) => {
				expect(responseCadastro.status).to.eq(201)
				var id = responseCadastro.body.uuid
				cy.excluir_comissoes(id).then((response) => {
					expect(response.status).to.eq(204)
				})
			})
		})

		it('Validar Delete no endpoint /api/comissoes/{uuid}/ com uuid invalido', () => {
			var id = 'responseCadastro.body.uuid'
			cy.excluir_comissoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Delete no endpoint /api/comissoes/{uuid}/ com uuid em branco', () => {
			var id = ''
			cy.excluir_comissoes(id).then((response) => {
				expect(response.status).to.eq(405)
				expect(response.statusText).to.eq("Method Not Allowed")
				expect(response.body.detail).to.eq("Method \"DELETE\" not allowed.")
			})
		})

	})

	context('Casos de teste para a rota de Put /api/comissoes/{uuid}/', () => {
		it('Validar Put no endpoint /api/comissoes/{uuid}/ com sucesso', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = { nome: "teste automatizado editado" }
				cy.alterar_comissoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.nome).to.eq(body.nome)
					expect(responseAlterar.body.id).to.exist
					expect(responseAlterar.body.uuid).to.exist
				cy.excluir_comissoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com nome em branco', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = { nome: "" }
				cy.alterar_comissoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq("This field may not be blank.")
				cy.excluir_comissoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

	})

	context('Casos de teste para a rota de Patch /api/comissoes/{uuid}/', () => {
		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com sucesso', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = { nome: "teste automatizado editado" }
				cy.editar_comissoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.nome).to.eq(body.nome)
					expect(responseAlterar.body.id).to.exist
					expect(responseAlterar.body.uuid).to.exist
				cy.excluir_comissoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com nome em branco', () => {
			var body = { nome: "teste automatizado" }
			cy.cadastrar_comissoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = { nome: "" }
				cy.editar_comissoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq("This field may not be blank.")
				cy.excluir_comissoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

	})

})