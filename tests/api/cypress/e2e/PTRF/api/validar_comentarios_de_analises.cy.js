/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/comentarios-de-analises/', () => {
		it('Validar Get no endpoint /api/comentarios-de-analises/ com sucesso sem parametros', () => {
			var id = ''
			cy.validar_comentarios_de_analises(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get /api/comentarios-de-analises/{uuid}/', () => {
		it('Validar Get no endpoint /api/comentarios-de-analises/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_comentarios_de_analises(id).then((response) => {
				expect(response.status).to.eq(200)
				id = response.body[0].uuid
				cy.validar_comentarios_de_analises(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.associacao).to.null
					expect(response.body.comentario).to.exist
					expect(response.body.notificado).to.exist
					expect(response.body.notificado_em).to.null
					expect(response.body.ordem).to.exist
					expect(response.body.periodo).to.null
					expect(response.body.prestacao_conta).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/comentarios-de-analises/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_comentarios_de_analises(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post /api/comentarios-de-analises/', () => {
		it('Validar Post no endpoint /api/comentarios-de-analises/ com sucesso', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.comentario).to.eq(body.comentario)
				expect(response.body.associacao).to.null
				expect(response.body.notificado).to.eq(false)
				expect(response.body.notificado_em).to.null
				expect(response.body.ordem).to.eq(1)
				expect(response.body.periodo).to.null
				expect(response.body.prestacao_conta).to.eq(body.prestacao_conta)
				expect(response.body.uuid).to.exist
				var id = response.body.uuid
				cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com prestação de conta invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.prestacao_conta[0]).to.eq(`“${body.prestacao_conta}” is not a valid UUID.`)
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com prestação de conta em branco', () => {
			var body = {
				prestacao_conta: "",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.detail).to.eq("É necessário enviar a prestação de contas ou associação e período.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com associacao invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: "dsad",
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com periodo invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: 'dsa',
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.periodo[0]).to.eq(`“${body.periodo}” is not a valid UUID.`)
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com ordem em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: '',
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.ordem[0]).to.eq("A valid integer is required.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com ordem invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 'dsf',
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.ordem[0]).to.eq("A valid integer is required.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com notificado invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: 'fdd',
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.notificado[0]).to.eq("Must be a valid boolean.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com notificado em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: '',
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.notificado[0]).to.eq("Must be a valid boolean.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com notificado_em em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: ''
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
			})
		})

		it('Validar Post no endpoint /api/comentarios-de-analises/ com notificado em com formato de data invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: '26/12/2021'
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
			})
		})

	})

	context('Casos de teste para a rota de Delete /api/comentarios-de-analises/{uuid}/', () => {
		it('Validar Delete no endpoint /api/comentarios-de-analises/{uuid}/ com sucesso', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((responseCadastro) => {
				expect(responseCadastro.status).to.eq(201)
				var id = responseCadastro.body.uuid
				cy.excluir_comentarios_de_analises(id).then((response) => {
					expect(response.status).to.eq(204)
				})
			})
		})

		it('Validar Delete no endpoint /api/comentarios-de-analises/{uuid}/ com uuid invalido', () => {
			var id = 'responseCadastro.body.uuid'
			cy.excluir_comentarios_de_analises(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Delete no endpoint /api/comentarios-de-analises/{uuid}/ com uuid em branco', () => {
			var id = ''
			cy.excluir_comentarios_de_analises(id).then((response) => {
				expect(response.status).to.eq(405)
				expect(response.statusText).to.eq("Method Not Allowed")
				expect(response.body.detail).to.eq("Method \"DELETE\" not allowed.")
			})
		})

	})

	context('Casos de teste para a rota de Put /api/comentarios-de-analises/{uuid}/', () => {

		it('Validar Put no endpoint /api/comentarios-de-analises/ com sucesso', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.comentario).to.eq(body.comentario)
					expect(responseAlterar.body.associacao).to.null
					expect(responseAlterar.body.notificado).to.eq(false)
					expect(responseAlterar.body.notificado_em).to.null
					expect(responseAlterar.body.ordem).to.eq(1)
					expect(responseAlterar.body.periodo).to.null
					expect(responseAlterar.body.prestacao_conta).to.eq(body.prestacao_conta)
					expect(responseAlterar.body.uuid).to.exist
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com prestação de conta invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.prestacao_conta[0]).to.eq(`“${body.prestacao_conta}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com prestação de conta em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
				expect(responseAlterar.status).to.eq(400)
				expect(responseAlterar.body.detail).to.eq("É necessário enviar a prestação de contas ou associação e período.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com associacao invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: "dsad",
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com periodo invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: 'fcdf',
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.periodo[0]).to.eq(`“${body.periodo}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com ordem em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: '',
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.ordem[0]).to.eq("A valid integer is required.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com ordem invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 'dsfs',
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.ordem[0]).to.eq("A valid integer is required.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com notificado invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: 'fsd',
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado[0]).to.eq("Must be a valid boolean.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com notificado em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: '',
					notificado_em: null
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado[0]).to.eq("Must be a valid boolean.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com notificado_em em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: null,
					notificado_em: ''
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Put no endpoint /api/comentarios-de-analises/ com notificado em com formato de data invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: null,
					notificado_em: '26/12/2021'
				}
				cy.alterar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

	})

	context('Casos de teste para a rota de Patch /api/comentarios-de-analises/{uuid}/', () => {

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com sucesso', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.comentario).to.eq(body.comentario)
					expect(responseAlterar.body.associacao).to.null
					expect(responseAlterar.body.notificado).to.eq(false)
					expect(responseAlterar.body.notificado_em).to.null
					expect(responseAlterar.body.ordem).to.eq(1)
					expect(responseAlterar.body.periodo).to.null
					expect(responseAlterar.body.prestacao_conta).to.eq(body.prestacao_conta)
					expect(responseAlterar.body.uuid).to.exist
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com prestação de conta invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.prestacao_conta[0]).to.eq(`“${body.prestacao_conta}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com prestação de conta em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
				expect(responseAlterar.status).to.eq(400)
				expect(responseAlterar.body.detail).to.eq("É necessário enviar a prestação de contas ou associação e período.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com associacao invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: "dsad",
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com periodo invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: 'fcdf',
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.periodo[0]).to.eq(`“${body.periodo}” is not a valid UUID.`)
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com ordem em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: '',
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.ordem[0]).to.eq("A valid integer is required.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com ordem invalida', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 'dsfs',
					comentario: "teste automatizado editado",
					notificado: false,
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.ordem[0]).to.eq("A valid integer is required.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com notificado invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: 'fsd',
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado[0]).to.eq("Must be a valid boolean.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com notificado em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: '',
					notificado_em: null
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado[0]).to.eq("Must be a valid boolean.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com notificado_em em branco', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: null,
					notificado_em: ''
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

		it('Validar Patch no endpoint /api/comentarios-de-analises/ com notificado em com formato de data invalido', () => {
			var body = {
				prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
				associacao: null,
				periodo: null,
				ordem: 1,
				comentario: "teste automatizado",
				notificado: false,
				notificado_em: null
			}
			cy.cadastrar_comentarios_de_analises(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					prestacao_conta: "225c1c9b-4c82-4d95-90a2-0cde3912d3a5",
					associacao: null,
					periodo: null,
					ordem: 1,
					comentario: "teste automatizado editado",
					notificado: null,
					notificado_em: '26/12/2021'
				}
				cy.editar_comentarios_de_analises(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.notificado_em[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
					cy.excluir_comentarios_de_analises(id).then((responseExcluir) => {
						expect(responseExcluir.status).to.eq(204)
					})
				})
			})

		})

	})

})