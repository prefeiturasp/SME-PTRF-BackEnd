/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')
	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get api/demonstrativo-financeiro/uuid/pdf/', () => {
		it('Validar Get no endpoint api/demonstrativo-financeiro/uuid/pdf/ com sucesso', () => {
			var id = '1a5743a0-8a12-4889-b5b9-bd3749db83cf'
			cy.validar_pdf_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

		it('Validar Get no endpoint api/demonstrativo-financeiro/uuid/pdf/ com uuid invalido', () => {
			var id = '8849c220-3dcb-4441-a810-162f5135'
			cy.validar_pdf_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(500)
			})
		})

		it('Validar Get no endpoint api/demonstrativo-financeiro/uuid/pdf/ com uuid em branco', () => {
			var id = ''
			cy.validar_pdf_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(404)
			})
		})
	})
	
	context('Casos de teste para a rota de Get /api/demonstrativo-financeiro/acoes/', () => {
		it('Validar Get no endpoint /api/demonstrativo-financeiro/acoes/ com sucesso', () => {
			var id = '?associacao_uuid=4a7bd512-000b-4bae-bc18-1578c10c1250&conta-associacao=313396ae-2b88-40a5-8f6d-86d99294c703&periodo_uuid=f5630a79-6f9f-4060-afb3-d0c86b903aec'
			cy.validar_acoes_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.info_acoes).to.exist
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/acoes/ com parametros invalidos', () => {
			var id = '?associacao_uuid=4a7bd512-000b-4bae-bc18-&conta-associacao=313396ae-2b88--8f6d-86d99294c703&periodo_uuid=f5630a79-6f9f-4060-afb3-'
			cy.validar_acoes_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(500)
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/acoes/ com parametros em branco', () => {
			var id = '?associacao_uuid=&conta-associacao=&periodo_uuid='
			cy.validar_acoes_demonstrativo_financeiro(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq("É necessário enviar o uuid do período, uuid da associação e o uuid da conta da associação.")
			})
		})

	})

	context('Casos de teste para a rota de Get /api/demonstrativo-financeiro/demonstrativo-info/', () => {
		it('Validar Get no endpoint /api/demonstrativo-financeiro/demonstrativo-info/ com sucesso', () => {
			var id = '?associacao_uuid=4a7bd512-000b-4bae-bc18-1578c10c1250&conta-associacao=313396ae-2b88-40a5-8f6d-86d99294c703&periodo_uuid=f5630a79-6f9f-4060-afb3-d0c86b903aec'
			cy.validar_demonstrativo_financeiro_demonstrativo_info(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.eq("Documento pendente de geração")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/demonstrativo-info/ sem associacao uuid', () => {
			var id = '?associacao_uuid=&conta-associacao=313396ae-2b88-40a5-8f6d-86d99294c703&periodo_uuid=f5630a79-6f9f-4060-afb3-d0c86b903aec'
			cy.validar_demonstrativo_financeiro_demonstrativo_info(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.eq("Documento pendente de geração")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/demonstrativo-info/ sem periodo uuid', () => {
			var id = '?associacao_uuid=4a7bd512-000b-4bae-bc18-1578c10c1250&conta-associacao=313396ae-2b88-40a5-8f6d-86d99294c703&periodo_uuid='
			cy.validar_demonstrativo_financeiro_demonstrativo_info(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.eq("Documento pendente de geração")
			})
		})

	})

	context('Casos de teste para a rota de Get /api/demonstrativo-financeiro/documento-final/', () => {
		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com sucesso', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36d04069ca&periodo=6a04e2c4-6769-4c56-abbc-edea7d87bead&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com conta associacao invalida', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36&periodo=6a04e2c4-6769-4c56-abbc-edea7d87bead&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com conta associacao em branco', () => {
			var id = '?conta-associacao=&periodo=6a04e2c4-6769-4c56-abbc-edea7d87bead&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq('É necessário enviar o uuid do período e o uuid da conta da associação.')
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com periodo invalido', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36d04069ca&periodo=6a04e2c4-6769-4c56-abbc-edea7&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com periodo em branco', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36d04069ca&periodo=&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.statusText).to.eq("Bad Request")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com formato arquivo invalido', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36d04069ca&periodo=6a04e2c4-6769-4c56-abbc-edea7d87bead&formato_arquivo=pdf'
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.statusText).to.eq("Bad Request")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-final/ com formato arquivo em branco', () => {
			var id = '?conta-associacao=202511ec-dae9-4c9a-ab96-1b36d04069ca&periodo=6a04e2c4-6769-4c56-abbc-edea7d87bead&formato_arquivo='
			cy.validar_demonstrativo_financeiro_documento_final(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})
		})

	})

	context('Casos de teste para a rota de Get /api/demonstrativo-financeiro/documento-previa/', () => {
		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com sucesso', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com conta associacao em branco', () => {
			var id = '?conta-associacao=&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq('É necessário enviar o uuid do período e o uuid da conta da associação.')
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com periodo invalido', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(404)
				expect(response.statusText).to.eq("Not Found")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com periodo em branco', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=&formato_arquivo=PDF'
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq('É necessário enviar o uuid do período e o uuid da conta da associação.')
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com formato arquivo em invalido', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&formato_arquivo=PF'
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametro_inválido")
				expect(response.body.mensagem).to.eq('O parâmetro formato_arquivo espera os valores XLSX ou PDF.')
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/documento-previa/ com formato arquivo em branco', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&formato_arquivo='
			cy.validar_demonstrativo_financeiro_documento_previa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.exist
			})
		})

	})

	context('Casos de teste para a rota de Get /api/demonstrativo-financeiro/previa/', () => {
		it('Validar Get no endpoint /api/demonstrativo-financeiro/previa/ com sucesso', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&data_inicio=2023-05-01&data_fim=2023-08-31'
			cy.validar_demonstrativo_financeiro_previa(id).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.mensagem).to.eq("Arquivo na fila para processamento.")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/previa/ com conta associação em branco', () => {
			var id = '?conta-associacao=&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&data_inicio=2023-05-01&data_fim=2023-08-31'
			cy.validar_demonstrativo_financeiro_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq("É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e fim do período.")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/previa/ com periodo em branco', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=&data_inicio=2023-05-01&data_fim=2023-08-31'
			cy.validar_demonstrativo_financeiro_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq("É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e fim do período.")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/previa/ com data inicio em branco', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&data_inicio=&data_fim=2023-08-31'
			cy.validar_demonstrativo_financeiro_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq("É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e fim do período.")
			})
		})

		it('Validar Get no endpoint /api/demonstrativo-financeiro/previa/ com data fim em branco', () => {
			var id = '?conta-associacao=24a04caf-8530-4824-b32b-56278a0c5891&periodo=f5630a79-6f9f-4060-afb3-d0c86b903aec&data_inicio=2023-05-01&data_fim='
			cy.validar_demonstrativo_financeiro_previa(id).then((response) => {
				expect(response.status).to.eq(400)
				expect(response.body.erro).to.eq("parametros_requeridos")
				expect(response.body.mensagem).to.eq("É necessário enviar o uuid da conta da associação o periodo_uuid e as datas de inicio e fim do período.")
			})
		})

	})
	
})

