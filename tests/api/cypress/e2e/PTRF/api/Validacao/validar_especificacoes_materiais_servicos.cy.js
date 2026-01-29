/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/especificacoes-materiais-servicos/', () => {
		it('Validar Get no endpoint /api/especificacoes-materiais-servicos/ com sucesso', () => {
			var id = ''
			cy.validar_especificacoes_materiais_servicos(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.results).to.exist
			})
		})
	})

	context('Casos de teste para a rota de Get /api/especificacoes-materiais-servicos/{uuid}/', () => {
		it('Validar Get no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_especificacoes_materiais_servicos(id).then((responseId) => {
				id = responseId.body.results[0].uuid
				cy.validar_especificacoes_materiais_servicos(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.aplicacao_recurso).to.exist
					expect(response.body.ativa).to.exist
					expect(response.body.descricao).to.exist
					expect(response.body.id).to.exist
					expect(response.body.tipo_custeio).to.exist
					expect(response.body.tipo_custeio_objeto).to.exist
					expect(response.body.uuid).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com uuid invalido', () => {
			var id = 'hdsh'
			cy.validar_especificacoes_materiais_servicos(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post /api/especificacoes-materiais-servicos/', () => {
		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com sucesso', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.aplicacao_recurso).to.eq(body.aplicacao_recurso)
				expect(response.body.ativa).to.eq(body.ativa)
				expect(response.body.descricao).to.eq(body.descricao)
				expect(response.body.tipo_custeio).to.eq(body.tipo_custeio)
				var id = response.body.uuid
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com descrição em branco', () => {
			var body = {
				descricao: "",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.descricao[0]).to.eq('This field may not be blank.')
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com decrição duplicada', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((responseCadastro) => {
				expect(responseCadastro.status).to.eq(201)
				var id = responseCadastro.body.uuid
				cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.erro).to.eq("Duplicated")
					expect(response.body.mensagem).to.eq("Esta especificação de material e serviço já existe.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com aplicacao recurso em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.aplicacao_recurso[0]).to.eq(`"" is not a valid choice.`)
			})
		})


		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com aplicacao recurso invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "teste",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.aplicacao_recurso[0]).to.eq(`"${body.aplicacao_recurso}" is not a valid choice.`)
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com tipo custeio zerado', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 0,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.tipo_custeio[0]).to.eq(`Invalid pk \"${body.tipo_custeio}\" - object does not exist.`)
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com tipo custeio invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 'Um',
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.tipo_custeio[0]).to.eq(`Incorrect type. Expected pk value, received str.`)
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com campo ativa invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: 'teste'
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.ativa[0]).to.eq("Must be a valid boolean.")
			})
		})

		it('Validar Post no endpoint /api/especificacoes-materiais-servicos/ com campo ativa em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: ''
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.ativa[0]).to.eq("Must be a valid boolean.")
			})
		})
	})

	context('Casos de teste para a rota de Delete /api/especificacoes-materiais-servicos/{uuid}/', () => {
		it('Validar Delete no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com sucesso', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((responseCadastro) => {
				expect(responseCadastro.status).to.eq(201)
				var id = responseCadastro.body.uuid
				cy.excluir_especificacoes_materiais_servicos(id).then((response) => {
					expect(response.status).to.eq(204)
				})
			})
		})

		it('Validar Delete no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com id invalido', () => {
			var id = 'teste'
			cy.excluir_especificacoes_materiais_servicos(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Delete no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com id em branco', () => {
			var id = ''
			cy.excluir_especificacoes_materiais_servicos(id).then((response) => {
				expect(response.status).to.eq(405)
				expect(response.statusText).to.eq('Method Not Allowed')
			})
		})
	})

	context('Casos de teste para a rota de Put /api/especificacoes-materiais-servicos/{uuid}/', () => {
		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com sucesso', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CUSTEIO",
					tipo_custeio: 2,
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(200)
					expect(responseAlteracao.body.aplicacao_recurso).to.eq(body.aplicacao_recurso)
					expect(responseAlteracao.body.ativa).to.eq(body.ativa)
					expect(responseAlteracao.body.descricao).to.eq(body.descricao)
					expect(responseAlteracao.body.tipo_custeio).to.eq(body.tipo_custeio)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com descrição em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "",
					aplicacao_recurso: "CUSTEIO",
					tipo_custeio: 2,
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.descricao[0]).to.eq("This field may not be blank.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com aplicacao recurso em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "",
					tipo_custeio: 2,
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.aplicacao_recurso[0]).to.eq(`"" is not a valid choice.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com aplicacao recurso invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "Teste",
					tipo_custeio: 2,
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.aplicacao_recurso[0]).to.eq(`"${body.aplicacao_recurso}" is not a valid choice.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com tipo custeio zerado', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 0,
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.tipo_custeio[0]).to.eq(`Invalid pk \"${body.tipo_custeio}\" - object does not exist.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com tipo custeio invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 'um',
					ativa: false
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.tipo_custeio[0]).to.eq(`Incorrect type. Expected pk value, received str.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com campo ativa invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 1,
					ativa: 'teste'
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.ativa[0]).to.eq("Must be a valid boolean.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Put no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com campo ativa em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 1,
					ativa: ''
				}
				cy.alterar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.ativa[0]).to.eq("Must be a valid boolean.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})
	})

	context('Casos de teste para a rota de Patch /api/especificacoes-materiais-servicos/{uuid}/', () => {
		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com sucesso', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CUSTEIO",
					tipo_custeio: 2,
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(200)
					expect(responseAlteracao.body.aplicacao_recurso).to.eq(body.aplicacao_recurso)
					expect(responseAlteracao.body.ativa).to.eq(body.ativa)
					expect(responseAlteracao.body.descricao).to.eq(body.descricao)
					expect(responseAlteracao.body.tipo_custeio).to.eq(body.tipo_custeio)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com descrição em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "",
					aplicacao_recurso: "CUSTEIO",
					tipo_custeio: 2,
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.descricao[0]).to.eq("This field may not be blank.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com aplicacao recurso em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "",
					tipo_custeio: 2,
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.aplicacao_recurso[0]).to.eq(`"" is not a valid choice.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com aplicacao recurso invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "Teste",
					tipo_custeio: 2,
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.aplicacao_recurso[0]).to.eq(`"${body.aplicacao_recurso}" is not a valid choice.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com tipo custeio zerado', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 0,
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.tipo_custeio[0]).to.eq(`Invalid pk \"${body.tipo_custeio}\" - object does not exist.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com tipo custeio invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 'um',
					ativa: false
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.tipo_custeio[0]).to.eq(`Incorrect type. Expected pk value, received str.`)
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com campo ativa invalido', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 1,
					ativa: 'teste'
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.ativa[0]).to.eq("Must be a valid boolean.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})

		it('Validar Patch no endpoint /api/especificacoes-materiais-servicos/{uuid}/ com campo ativa em branco', () => {
			var body = {
				descricao: "Teste Automacao",
				aplicacao_recurso: "CAPITAL",
				tipo_custeio: 1,
				ativa: true
			}
			cy.cadastrar_especificacoes_materiais_servicos(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				var body = {
					descricao: "Teste Automacao Edicao",
					aplicacao_recurso: "CAPITAL",
					tipo_custeio: 1,
					ativa: ''
				}
				cy.editar_especificacoes_materiais_servicos(body, id).then((responseAlteracao) => {
					expect(responseAlteracao.status).to.eq(400)
					expect(responseAlteracao.body.ativa[0]).to.eq("Must be a valid boolean.")
				})
				cy.excluir_especificacoes_materiais_servicos(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})
			})
		})
	})

	context('Casos de teste para a rota de Get /api/especificacoes-materiais-servicos/tabelas/', () => {
		it('Validar Get no endpoint /api/especificacoes-materiais-servicos/tabelas/ com sucesso', () => {
			cy.validar_tabelas_especificacoes_materiais_servicos().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.aplicacao_recursos).to.exist
				expect(response.body.tipos_custeio).to.exist
			})
		})

	})

})

