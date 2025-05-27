/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Post api/receitas-previstas-paa/', () => {
		it('Validar Post no endpoint api/receitas-previstas-paa/ com sucesso', () => {
			var body = {
				acao_associacao: 962,
				previsao_valor_capital: "1",
				previsao_valor_custeio: "1",
				previsao_valor_livre: "1"
			}
			cy.cadastrar_receitas_previstas_paa(body).then((response) => {
				expect(response.status).to.eq(201)
				expect(response.body.acao_associacao).to.eq(body.acao_associacao)
				expect(response.body.previsao_valor_capital).to.contains(body.previsao_valor_capital)
				expect(response.body.previsao_valor_custeio).to.contains(body.previsao_valor_custeio)
				expect(response.body.previsao_valor_livre).to.contains(body.previsao_valor_livre)
				expect(response.body).to.exist
			})
		})

		it('Validar Post no endpoint api/receitas-previstas-paa/ com acao associacao invalida', () => {
			var body = {
				acao_associacao: 'treze',
				previsao_valor_capital: "1",
				previsao_valor_custeio: "1",
				previsao_valor_livre: "1"
			}
			cy.cadastrar_receitas_previstas_paa(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.acao_associacao[0]).to.eq("Incorrect type. Expected pk value, received str.");
			})
		})

		it('Validar Post no endpoint api/receitas-previstas-paa/ com acao associacao em branco', () => {
			var body = {
				acao_associacao: '',
				previsao_valor_capital: "1",
				previsao_valor_custeio: "1",
				previsao_valor_livre: "1"
			}
			cy.cadastrar_receitas_previstas_paa(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.acao_associacao[0]).to.eq("O campo Ação de Associação é obrigatório.");
			})
		})

		it('Validar Post no endpoint api/receitas-previstas-paa/ com valores invalidos nos campos de valores', () => {
			var body = {
				acao_associacao: 975,
				previsao_valor_capital: "treze",
				previsao_valor_custeio: "treze",
				previsao_valor_livre: "treze"
			}
			cy.cadastrar_receitas_previstas_paa(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.previsao_valor_capital[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_custeio[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_livre[0]).to.eq("A valid number is required.");
			})
		})

		it('Validar Post no endpoint api/receitas-previstas-paa/ com valores em branco nos campos de valores', () => {
			var body = {
				acao_associacao: 975,
				previsao_valor_capital: "",
				previsao_valor_custeio: "",
				previsao_valor_livre: ""
			}
			cy.cadastrar_receitas_previstas_paa(body).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.previsao_valor_capital[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_custeio[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_livre[0]).to.eq("A valid number is required.");
			})
		})

	})

	context('Casos de teste para a rota de Patch api/receitas-previstas-paa/{uuid}/', () => {
		it('Validar Patch no endpoint api/receitas-previstas-paa/{uuid}/ com sucesso', () => {
			var id = '69e3d407-0e68-4524-b347-f3c93d97030b'
			var body_alteracao = {
				acao_associacao: 962,
				previsao_valor_capital: "2",
				previsao_valor_custeio: "2",
				previsao_valor_livre: "2"
			}
			cy.editar_receitas_previstas_paa(body_alteracao, id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.previsao_valor_capital).to.contains(body_alteracao.previsao_valor_capital)
				expect(response.body.previsao_valor_custeio).to.contains(body_alteracao.previsao_valor_custeio)
				expect(response.body.previsao_valor_livre).to.contain(body_alteracao.previsao_valor_livre)
			})
		})

		it('Validar Patch no endpoint api/receitas-previstas-paa/{uuid}/ com acao associacao invalida', () => {
			var id = '69e3d407-0e68-4524-b347-f3c93d97030b'
			var body_alteracao = {
				acao_associacao: 'treze',
				previsao_valor_capital: "2",
				previsao_valor_custeio: "2",
				previsao_valor_livre: "2"
			}
			cy.editar_receitas_previstas_paa(body_alteracao, id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.acao_associacao[0]).to.eq("Incorrect type. Expected pk value, received str.");
			})
		})

		it('Validar Patch no endpoint api/receitas-previstas-paa/{uuid}/ com valores invalidos nos campos de valores', () => {
			var id = '69e3d407-0e68-4524-b347-f3c93d97030b'
			var body_alteracao = {
				acao_associacao: '',
				previsao_valor_capital: "trreze",
				previsao_valor_custeio: "treze",
				previsao_valor_livre: "treze"
			}
			cy.editar_receitas_previstas_paa(body_alteracao, id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.previsao_valor_capital[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_custeio[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_livre[0]).to.eq("A valid number is required.");
			})
		})

		it('Validar Patch no endpoint api/receitas-previstas-paa/{uuid}/ com valores em branco nos campos de valores', () => {
			var id = '69e3d407-0e68-4524-b347-f3c93d97030b'
			var body_alteracao = {
				acao_associacao: '',
				previsao_valor_capital: "",
				previsao_valor_custeio: "",
				previsao_valor_livre: ""
			}
			cy.editar_receitas_previstas_paa(body_alteracao, id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.previsao_valor_capital[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_custeio[0]).to.eq("A valid number is required.");
				expect(response.body.previsao_valor_livre[0]).to.eq("A valid number is required.");
			})
		})

	})

	context('Casos de teste para a rota de Get api/receitas-previstas-paa/', () => {
		it('Validar Get no endpoint api/receitas-previstas-paa/ com sucesso sem parametro', () => {
			var id = ''
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
				expect(response.body.results).to.exist
			})
		})

		it('Validar Get no endpoint api/receitas-previstas-paa/ com sucesso somente com o parametro acao nome', () => {
			var id = '?acao_nome=PTRF%20B%C3%A1sico'
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
				expect(response.body.results).to.exist
			})
		})

		it('Validar Get no endpoint api/receitas-previstas-paa/ com sucesso somente com o parametro acao uuid', () => {
			var id = '?acao_uuid=bdcbc8ce-7bab-48b3-959a-f866c6644579'
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
				expect(response.body.results).to.exist
			})
		})

		it('Validar Get no endpoint api/receitas-previstas-paa/ com dados invalidos', () => {
			var id = '?acao_nome=dsad&acao_uuid=bdcbc8ce-7bab-48b3-959a-f866c6644579&associacao_nome=dasd&associacao_uuid=bdcbc8ce-7bab-48b3-959a-f866c6644579'
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
				expect(response.body.results).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get api/receitas-previstas-paa/uuid', () => {
		it('Validar Get no endpoint api/receitas-previstas-paa/uuid com sucesso', () => {
			var id = '69e3d407-0e68-4524-b347-f3c93d97030b'
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
				expect(response.body.uuid).to.eq(id)
			})
		})

		it('Validar Get no endpoint api/acoes-associacoes/uuid com uuid invalido', () => {
			var id = 'f234e1d2-d894-4445-bdbd-e01fc4db2'
			cy.validar_receitas_previstas_paa(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})
		})

	})

})

