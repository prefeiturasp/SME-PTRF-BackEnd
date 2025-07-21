/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})
	context('Casos de teste para a rota de Get api/acoes/', () => {
		it('Validar retorno do endpoint api/acoes com sucesso', () => {
			var id = ''
			cy.validar_acoes(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.statusText).to.eq('OK')
			})
		})
	})

	context('Casos de teste para a rota Get api/acoes/{uuid}/', () => {
		it('Validar retorno do endpoint api/acoes/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_acoes(id).then((responseTodasAcoes) => {
				id = responseTodasAcoes.body[0].uuid
				cy.validar_acoes(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.aceita_capital).to.exist
					expect(response.body.aceita_custeio).to.exist
					expect(response.body.aceita_livre).to.exist
					expect(response.body.e_recursos_proprios).to.exist
					expect(response.body.id).to.exist
					expect(response.body.nome).to.exist
					expect(response.body.posicao_nas_pesquisas).to.exist
					expect(response.body.uuid).to.eq(id)
				})
			})
		})

		it('Validar retorno do endpoint api/acoes/{uuid}/ com uuid invalido', () => {
			var id = '1'
			cy.validar_acoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post api/acoes/', () => {
		it('Validar post no endpoint api/acoes com sucesso', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}

			cy.cadastrar_acoes(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.aceita_capital).to.eq(body.aceita_capital)
				expect(response.body.aceita_custeio).to.eq(body.aceita_custeio)
				expect(response.body.aceita_livre).to.eq(body.aceita_livre)
				expect(response.body.e_recursos_proprios).to.eq(body.e_recursos_proprios)
				expect(response.body.nome).to.eq(body.nome)
				expect(response.body.posicao_nas_pesquisas).to.eq(body.posicao_nas_pesquisas)
				var id = response.body.uuid
				cy.excluir_acoes(id).then((responseExclusao) => {
					expect(responseExclusao.status).to.eq(204)
				})

			})
		})

		it('Validar post no endpoint api/acoes com campo nome em branco', () => {
			var body = {
				nome: "",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}

			cy.cadastrar_acoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.nome[0]).to.eq('This field may not be blank.')
			})
		})

		it('Validar post no endpoint api/acoes com campo posicao_nas_pesquisas com mais de 10 posições', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "testetestee",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}

			cy.cadastrar_acoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.posicao_nas_pesquisas[0]).to.eq('Ensure this field has no more than 10 characters.')
			})
		})

		it('Validar post no endpoint api/acoes com os campos e_recursos_proprios, aceita_capital, aceita_custeio, aceita_livre em branco', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: '',
				posicao_nas_pesquisas: "teste",
				aceita_capital: '',
				aceita_custeio: '',
				aceita_livre: ''
			}

			cy.cadastrar_acoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.aceita_capital[0]).to.eq("Must be a valid boolean.")
				expect(response.body.aceita_custeio[0]).to.eq("Must be a valid boolean.")
				expect(response.body.aceita_livre[0]).to.eq("Must be a valid boolean.")
				expect(response.body.e_recursos_proprios[0]).to.eq("Must be a valid boolean.")
			})
		})
	})

	context('Casos de teste para a rota de Delete api/acoes/', () => {
		it('Validar exclusao no endpoint api/acoes com sucesso', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}

			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var id = responseCriacao.body.uuid
				cy.excluir_acoes(id).then((response) => {
					expect(response.status).to.eq(204)
					expect(response.statusText).to.eq("No Content")
				})

			})
		})

		it('Validar exclusao no endpoint api/acoes com id inexistente', () => {

			var id = 'testeNaoExiste'
			cy.excluir_acoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})

		})

		it('Validar exclusao no endpoint api/acoes com id em branco', () => {

			var id = ''
			cy.excluir_acoes(id).then((response) => {
				expect(response.status).to.eq(405)
				expect(response.body.detail).to.eq(`Method "DELETE" not allowed.`)
				expect(response.statusText).to.eq("Method Not Allowed")
			})

		})

	})

	context('Casos de teste para a rota de Edição Put api/acoes/', () => {
		it('Validar edição Put no endpoint api/acoes com sucesso', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado editado",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "teste e",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.editar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.aceita_capital).to.eq(body.aceita_capital)
					expect(response.body.aceita_custeio).to.eq(body.aceita_custeio)
					expect(response.body.aceita_livre).to.eq(body.aceita_livre)
					expect(response.body.e_recursos_proprios).to.eq(body.e_recursos_proprios)
					expect(response.body.nome).to.eq(body.nome)
					expect(response.body.posicao_nas_pesquisas).to.eq(body.posicao_nas_pesquisas)
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição Put no endpoint api/acoes com campo nome em branco', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "teste e",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.editar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.nome[0]).to.eq('This field may not be blank.')
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição Put no endpoint api/acoes com os campos e_recursos_proprios, aceita_capital, aceita_custeio, aceita_livre em branco', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado",
					e_recursos_proprios: '',
					posicao_nas_pesquisas: "teste e",
					aceita_capital: '',
					aceita_custeio: '',
					aceita_livre: ''
				}
				var id = responseCriacao.body.uuid
				cy.editar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.aceita_capital[0]).to.eq("Must be a valid boolean.")
					expect(response.body.aceita_custeio[0]).to.eq("Must be a valid boolean.")
					expect(response.body.aceita_livre[0]).to.eq("Must be a valid boolean.")
					expect(response.body.e_recursos_proprios[0]).to.eq("Must be a valid boolean.")
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição Put no endpoint api/acoes com campo posicao_nas_pesquisas com mais de 10 posições', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "testetestee",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.editar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.posicao_nas_pesquisas[0]).to.eq('Ensure this field has no more than 10 characters.')
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

	})

	context('Casos de teste para a rota de Edição Patch api/acoes/', () => {
		it('Validar edição Patch no endpoint api/acoes com sucesso', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado editado",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "teste e",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.alterar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.aceita_capital).to.eq(body.aceita_capital)
					expect(response.body.aceita_custeio).to.eq(body.aceita_custeio)
					expect(response.body.aceita_livre).to.eq(body.aceita_livre)
					expect(response.body.e_recursos_proprios).to.eq(body.e_recursos_proprios)
					expect(response.body.nome).to.eq(body.nome)
					expect(response.body.posicao_nas_pesquisas).to.eq(body.posicao_nas_pesquisas)
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição patch no endpoint api/acoes com campo nome em branco', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "teste e",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.alterar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.nome[0]).to.eq('This field may not be blank.')
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição Patch no endpoint api/acoes com os campos e_recursos_proprios, aceita_capital, aceita_custeio, aceita_livre em branco', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado",
					e_recursos_proprios: '',
					posicao_nas_pesquisas: "teste e",
					aceita_capital: '',
					aceita_custeio: '',
					aceita_livre: ''
				}
				var id = responseCriacao.body.uuid
				cy.alterar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.aceita_capital[0]).to.eq("Must be a valid boolean.")
					expect(response.body.aceita_custeio[0]).to.eq("Must be a valid boolean.")
					expect(response.body.aceita_livre[0]).to.eq("Must be a valid boolean.")
					expect(response.body.e_recursos_proprios[0]).to.eq("Must be a valid boolean.")
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

		it('Validar edição Patch no endpoint api/acoes com campo posicao_nas_pesquisas com mais de 10 posições', () => {
			var body = {
				nome: "teste automatizado",
				e_recursos_proprios: true,
				posicao_nas_pesquisas: "teste",
				aceita_capital: true,
				aceita_custeio: true,
				aceita_livre: true
			}
			cy.cadastrar_acoes(body).then((responseCriacao) => {
				expect(responseCriacao.status).to.eq(201)
				var body = {
					nome: "teste automatizado",
					e_recursos_proprios: false,
					posicao_nas_pesquisas: "testetestee",
					aceita_capital: false,
					aceita_custeio: false,
					aceita_livre: false
				}
				var id = responseCriacao.body.uuid
				cy.alterar_acoes(body, id).then((response) => {
					expect(response.status).to.eq(400)
					expect(response.body.posicao_nas_pesquisas[0]).to.eq('Ensure this field has no more than 10 characters.')
					cy.excluir_acoes(id).then((response) => {
						expect(response.status).to.eq(204)
						expect(response.statusText).to.eq("No Content")
					})
				})

			})
		})

	})

	context('Casos de teste para a rota Get api/acoes/{uuid}/associacoes-nao-vinculadas/', () => {
		var id = ''
		it('Validar retorno do endpoint api/acoes/{uuid}/associacoes-nao-vinculadas/ com sucesso', () => {
			cy.validar_acoes(id).then((responseTodasAcoes) => {
				id = responseTodasAcoes.body[0].uuid
				cy.validar_acoes_com_associacoes_nao_vinculadas(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body[0].cnpj).to.exist
					expect(response.body[0].data_de_encerramento).to.be.null
					expect(response.body[0].encerrada).to.exist
					expect(response.body[0].informacoes).to.exist
					expect(response.body[0].nome).to.exist
					expect(response.body[0].status_valores_reprogramados).to.exist
					expect(response.body[0].tooltip_data_encerramento).to.be.null
					expect(response.body[0].unidade.codigo_eol).to.exist
					expect(response.body[0].unidade.nome_com_tipo).to.exist
					expect(response.body[0].unidade.nome_dre).to.exist
					expect(response.body[0].unidade.uuid).to.exist
					expect(response.body[0].uuid).to.exist
				})
			})
		})

		it('Validar retorno do endpoint api/acoes/{uuid}/associacoes-nao-vinculadas/ com uuid invalido', () => {
			cy.validar_acoes(id).then(() => {
				id = 'fd5f4'
				cy.validar_acoes_com_associacoes_nao_vinculadas(id).then((response) => {
					expect(response.status).to.eq(404)
					expect(response.statusText).to.eq('Not Found')
				})
			})
		})

	})

	context('Casos de teste para a rota Get api/acoes/{uuid}/associacoes-nao-vinculadas-por-nome/{nome}/', () => {
		it('Validar retorno do endpoint api/acoes/{uuid}/associacoes-nao-vinculadas-por-nome/{nome}/ com nome com vinculo', () => {
			var id = ''
			cy.validar_acoes(id).then((responseTodasAcoes) => {
				id = responseTodasAcoes.body[0].uuid
				var nome = responseTodasAcoes.body[0].nome
				cy.validar_acoes_com_associacoes_nao_vinculadas_por_nome(id, nome).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body).to.exist
				})
			})
		})

		it('Validar retorno do endpoint api/acoes/{uuid}/associacoes-nao-vinculadas-por-nome/{nome}/ com sucesso', () => {
			var id = ''
			cy.validar_acoes(id).then((responseTodasAcoes) => {
				id = responseTodasAcoes.body[0].uuid
				var nome = 'te'
				cy.validar_acoes_com_associacoes_nao_vinculadas_por_nome(id, nome).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body).to.exist
				})
			})
		})

	})
})

