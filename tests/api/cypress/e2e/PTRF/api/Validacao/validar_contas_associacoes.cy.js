/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get /api/contas-associacoes/', () => {
		it('Validar Get no endpoint /api/contas-associacoes/ com sucesso', () => {
			var id = ''
			cy.validar_contas_associacoes(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.results).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get /api/contas-associacoes/{uuid}/', () => {
		it('Validar Get no endpoint /api/contas-associacoes/{uuid}/ com sucesso', () => {
			var id = ''
			cy.validar_contas_associacoes(id).then((response) => {
				expect(response.status).to.eq(200)
				id = response.body.results[0].uuid
				cy.validar_contas_associacoes(id).then((response) => {
					expect(response.status).to.eq(200)
					expect(response.body.uuid).to.eq(id)
					expect(response.body.id).to.exist
					expect(response.body).to.exist
				})
			})
		})

		it('Validar Get no endpoint /api/contas-associacoes/{uuid}/ com uuid invalido', () => {
			var id = 'fd4'
			cy.validar_contas_associacoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})
	})

	context('Casos de teste para a rota de Post /api/contas-associacoes/', () => {
		it('Validar Post no endpoint /api/contas-associacoes/ com sucesso', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.banco_nome).to.eq(body.banco_nome)
				expect(response.body.agencia).to.eq(body.agencia)
				expect(response.body.numero_conta).to.eq(body.numero_conta)
				expect(response.body.numero_cartao).to.eq(body.numero_cartao)
				expect(response.body.data_inicio).to.eq(body.data_inicio)
				expect(response.body.associacao).to.eq(body.associacao)
				expect(response.body.tipo_conta).to.eq(body.tipo_conta)
				expect(response.body.status).to.eq(body.status)
				var id = response.body.uuid
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com associacao invalida', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com associacao em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.associacao[0]).to.eq(`This field may not be null.`)
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com tipo conta invalida', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c2",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.tipo_conta[0]).to.eq(`“${body.tipo_conta}” is not a valid UUID.`)
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com tipo conta em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.tipo_conta[0]).to.eq("This field may not be null.")
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com status em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: ""
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.status[0]).to.eq("\"\" is not a valid choice.")
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com status invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "teste"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.status[0]).to.eq(`\"${body.status}\" is not a valid choice.`)
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com banco nome com mais de 50 posições', () => {
			var body = {
				banco_nome: "teste automatizadokkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
				agencia: "automatizado",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.banco_nome[0]).to.eq("Ensure this field has no more than 50 characters.")
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com agencia com mais de 15 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste automatkkk",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.agencia[0]).to.eq("Ensure this field has no more than 15 characters.")
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com numero conta com mais de 30 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste auto",
				numero_conta: "teste automatkkkkkkkkkkkkkkkkkk",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.numero_conta[0]).to.eq("Ensure this field has no more than 30 characters.")
			})
		})

		it('Validar Post no endpoint /api/contas-associacoes/ com numero cartao com mais de 80 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste auto",
				numero_conta: "1290967-X",
				numero_cartao: "teste automatkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.numero_cartao[0]).to.eq("Ensure this field has no more than 80 characters.")
			})
		})
		
		it('Validar Post no endpoint /api/contas-associacoes/ com data inicio em formato invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste auto",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "24-01-2025",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.data_inicio[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
			})
		})
	})

	context('Casos de teste para a rota de Delete /api/contas-associacoes/{uuid}/', () => {
		it('Validar Delete no endpoint /api/contas-associacoes/{uuid}/ com sucesso', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((responseCadastro) => {
				expect(responseCadastro.status).to.eq(201)
				var id = responseCadastro.body.uuid
				cy.excluir_contas_associacoes(id).then((response) => {
					expect(response.status).to.eq(204)
				})
			})
		})

		it('Validar Delete no endpoint /api/contas-associacoes/{uuid}/ com uuid invalido', () => {
			var id = 'responseCadastro.body.uuid'
			cy.excluir_contas_associacoes(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq('Not Found')
			})
		})

		it('Validar Delete no endpoint /api/contas-associacoes/{uuid}/ com uuid em branco', () => {
			var id = ''
			cy.excluir_contas_associacoes(id).then((response) => {
				expect(response.status).to.eq(405)
				expect(response.statusText).to.eq("Method Not Allowed")
				expect(response.body.detail).to.eq("Method \"DELETE\" not allowed.")
			})
		})

	})

	context('Casos de teste para a rota de Put /api/contas-associacoes/{uuid}/', () => {
		it('Validar Put no endpoint /api/contas-associacoes/{uuid}/ com sucesso', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.banco_nome).to.eq(body.banco_nome)
					expect(responseAlterar.body.agencia).to.eq(body.agencia)
					expect(responseAlterar.body.numero_conta).to.eq(body.numero_conta)
					expect(responseAlterar.body.numero_cartao).to.eq(body.numero_cartao)
					expect(responseAlterar.body.data_inicio).to.eq(body.data_inicio)
					expect(responseAlterar.body.associacao_dados.uuid).to.eq(body.associacao)
					expect(responseAlterar.body.tipo_conta).to.eq(body.tipo_conta)
					expect(responseAlterar.body.status).to.eq(body.status)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com associacao invalida', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com associacao em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq("This field may not be null.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		
		it('Validar Put no endpoint /api/comissoes/{uuid}/ com tipo conta invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.tipo_conta[0]).to.eq(`“${body.tipo_conta}” is not a valid UUID.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com tipo conta em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.tipo_conta[0]).to.eq("This field may not be null.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com Status em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: ""
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.status[0]).to.eq(`\"\" is not a valid choice.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com Status invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "teste"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.status[0]).to.eq(`"${body.status}" is not a valid choice.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com banco nome com mais de 50 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizadokkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.banco_nome[0]).to.eq("Ensure this field has no more than 50 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com agencia com mais de 15 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editadoooooooooo",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.agencia[0]).to.eq("Ensure this field has no more than 15 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com numero conta com mais de 30 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "teste automatkkkkkkkkkkkkkkkkkk",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.numero_conta[0]).to.eq("Ensure this field has no more than 30 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com numero cartao com mais de 80 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "5456 3161 8766 6985",
					numero_cartao: "teste automatkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.numero_cartao[0]).to.eq("Ensure this field has no more than 80 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Put no endpoint /api/comissoes/{uuid}/ com data inicio em formato invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "25-03-2024",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.alterar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.data_inicio[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

	})

	context('Casos de teste para a rota de Patch /api/contas-associacoes/{uuid}/', () => {
		it('Validar Patch no endpoint /api/contas-associacoes/{uuid}/ com sucesso', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(200)
					expect(responseAlterar.body.banco_nome).to.eq(body.banco_nome)
					expect(responseAlterar.body.agencia).to.eq(body.agencia)
					expect(responseAlterar.body.numero_conta).to.eq(body.numero_conta)
					expect(responseAlterar.body.numero_cartao).to.eq(body.numero_cartao)
					expect(responseAlterar.body.data_inicio).to.eq(body.data_inicio)
					expect(responseAlterar.body.associacao_dados.uuid).to.eq(body.associacao)
					expect(responseAlterar.body.tipo_conta).to.eq(body.tipo_conta)
					expect(responseAlterar.body.status).to.eq(body.status)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com associacao invalida', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq(`“${body.associacao}” is not a valid UUID.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com associacao em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.associacao[0]).to.eq("This field may not be null.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		
		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com tipo conta invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.tipo_conta[0]).to.eq(`“${body.tipo_conta}” is not a valid UUID.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com tipo conta em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.tipo_conta[0]).to.eq("This field may not be null.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com Status em branco', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: ""
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.status[0]).to.eq(`\"\" is not a valid choice.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com Status invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado editado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "teste"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.status[0]).to.eq(`"${body.status}" is not a valid choice.`)
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com banco nome com mais de 50 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizadokkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.banco_nome[0]).to.eq("Ensure this field has no more than 50 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com agencia com mais de 15 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editadoooooooooo",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.agencia[0]).to.eq("Ensure this field has no more than 15 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com numero conta com mais de 30 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "teste automatkkkkkkkkkkkkkkkkkk",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.numero_conta[0]).to.eq("Ensure this field has no more than 30 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com numero cartao com mais de 80 posições', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "5456 3161 8766 6985",
					numero_cartao: "teste automatkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
					data_inicio: "2025-03-24",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.numero_cartao[0]).to.eq("Ensure this field has no more than 80 characters.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

		it('Validar Patch no endpoint /api/comissoes/{uuid}/ com data inicio em formato invalido', () => {
			var body = {
				banco_nome: "teste automatizado",
				agencia: "teste aut",
				numero_conta: "1290967-X",
				numero_cartao: "5456 3161 8766 6985",
				data_inicio: "2025-03-24",
				associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
				tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
				status: "ATIVA"
			  }
			cy.cadastrar_contas_associacoes(body).then((response) => {
				expect(response.status).to.eq(201)
				var id = response.body.uuid
				body = {
					banco_nome: "teste automatizado",
					agencia: "editado",
					numero_conta: "1290967-X",
					numero_cartao: "5456 3161 8766 6985",
					data_inicio: "25-03-2024",
					associacao: "ea536bcb-397e-4d2c-8fe5-319cbc4b0254",
					tipo_conta: "581af94a-d8dd-466d-9738-2be24655c221",
					status: "ATIVA"
				  }
				cy.editar_contas_associacoes(body, id).then((responseAlterar) => {
					expect(responseAlterar.status).to.eq(400)
					expect(responseAlterar.body.data_inicio[0]).to.eq("Date has wrong format. Use one of these formats instead: YYYY-MM-DD.")
				cy.excluir_contas_associacoes(id).then((responseExcluir) => {
					expect(responseExcluir.status).to.eq(204)
				})
			})
			})
		})

	})

	context('Casos de teste para a rota de Get /api/contas-associacoes/filtros/', () => {
		it('Validar Get no endpoint /api/contas-associacoes/filtros/ com sucesso', () => {
			cy.validar_contas_associacoes_filtros().then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.status).to.exist
				expect(response.body.tipos_contas).to.exist
			})
		})

	})


})