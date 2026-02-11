/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/faq-categorias/', () => {
		it('Validar Get no endpoint /api/faq-categorias/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var idGet = ''
				var id = response.body.uuid
				cy.validar_faq_categorias(idGet).then((response) => {
					cy.log(response)
					expect(response.status).to.eq(200)
					expect(response.body[0].nome).to.eq(body.nome)
					expect(response.body[0].uuid).to.exist
				})
				cy.excluir_faq_categorias(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})
	})

	context('Casos de teste para a rota de Get /api/faq-categorias/{uuid}/', () => {
		it('Validar Get no endpoint /api/faq-categorias/{uuid}/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				cy.validar_faq_categorias(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.nome).to.eq(body.nome)
					expect(response.body.uuid).to.exist
				})
				cy.excluir_faq_categorias(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})

		it('Validar Get no endpoint /api/faq-categorias/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_faq_categorias(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post /api/faq-categorias/', () => {
		it('Validar Post no endpoint /api/faq-categorias/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.nome).to.eq(body.nome)
				expect(response.body.uuid).to.exist
				var id = response.body.uuid
				cy.excluir_faq_categorias(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/faq-categorias/ com campo nome em branco', () => {
			var body = {
				nome: "",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.nome[0]).to.eq('This field may not be blank.')
			})
		})

		it('Validar Post no endpoint /api/faq-categorias/ campo nome com mais de 200 posições', () => {
			var body = {
				nome: "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.nome[0]).to.eq('Ensure this field has no more than 200 characters.')
			})
		})

	})

	context('Casos de teste para a rota de Delete /api/faq-categorias/{uuid}/', () => {
		it('Validar Delete no endpoint /api/faq-categorias/{uuid}/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				cy.excluir_faq_categorias(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
					expect(responseExcluir.statusText).to.eq('No Content')
				})
			})
		})

		it('Validar Delete no endpoint /api/faq-categorias/{uuid}/ com uuid invalido', () => {
			var id = 'gfhfgdhghdf'
			cy.excluir_faq_categorias(id).then((responseExcluir) => {
				expect(responseExcluir.status).to.eq(404)
				expect(responseExcluir.statusText).to.eq('Not Found')
			})
		})

		it('Validar Delete no endpoint /api/faq-categorias/{uuid}/ com uuid em branco', () => {
			var id = ''
			cy.excluir_faq_categorias(id).then((responseExcluir) => {
				expect(responseExcluir.status).to.eq(405)
				expect(responseExcluir.statusText).to.eq("Method Not Allowed")
				expect(responseExcluir.body.detail).to.eq("Method \"DELETE\" not allowed.")
			})
		})

	})

	context('Casos de teste para a rota de Put /api/faq-categorias/{uuid}/', () => {
		it('Validar Put no endpoint /api/faq-categorias/{uuid}/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "teste automatizado editado",
				}
				cy.alterar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.nome).to.eq(body.nome)
					expect(responseAlterar.body.uuid).to.exist
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

		it('Validar Put no endpoint /api/faq-categorias/{uuid}/ campo nome em branco', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "",
				}
				cy.alterar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq('This field may not be blank.')
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

		it('Validar Put no endpoint /api/faq-categorias/{uuid}/ campo nome com mais de 200 posições', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
				}
				cy.alterar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq("Ensure this field has no more than 200 characters.")
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

	})

	context('Casos de teste para a rota de Patch /api/faq-categorias/{uuid}/', () => {
		it('Validar Patch no endpoint /api/faq-categorias/{uuid}/ com sucesso', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "teste automatizado editado",
				}
				cy.editar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.nome).to.eq(body.nome)
					expect(responseAlterar.body.uuid).to.exist
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

		it('Validar Patch no endpoint /api/faq-categorias/{uuid}/ campo nome em branco', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "",
				}
				cy.editar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq('This field may not be blank.')
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

		it('Validar Patch no endpoint /api/faq-categorias/{uuid}/ campo nome com mais de 200 posições', () => {
			var body = {
				nome: "teste automatizado",
			}
			cy.cadastrar_faq_categorias(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					nome: "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
				}
				cy.editar_faq_categorias(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.nome[0]).to.eq("Ensure this field has no more than 200 characters.")
					cy.excluir_faq_categorias(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})
		})

	})

})