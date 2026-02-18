/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
	var usuario = Cypress.config('usuario_homol_sme')
	var senha = Cypress.config('senha_homol')

	before(() => {
		cy.autenticar_login(usuario, senha)
	})

	context('Casos de teste para a rota de Get api/ano-analise-regularidade/', () => {
		it('Validar Get no endpoint api/ano-analise-regularidade/ com sucesso', () => {
			var ano = ''
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.be.not.null
			})
		})

		it('Validar que a resposta retorna uma lista de anos', () => {
			var ano = ''
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body).to.be.an('array')
				expect(response.body.length).to.be.greaterThan(0)
			})
		})

		it('Validar estrutura básica dos itens retornados', () => {
			var ano = ''
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body[0]).to.have.property('ano')
			})
		})
	})

	context('Casos de teste para a rota de Get api/ano-analise-regularidade/{ano}/', () => {
		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com sucesso', () => {
			var ano = 2023
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.ano).to.eq(ano)
			})
		})

		it('Validar que o campo ano retornado é numérico', () => {
			var ano = 2023
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(200)
				expect(response.body.ano).to.be.a('number')
			})
		})

		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com valor ano invalido', () => {
			var ano = 'teste'
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com valor ano inexistente', () => {
			var ano = '21'
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com valor ano maior que ano atual', () => {
			var ano = '2200'
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com ano negativo', () => {
			var ano = '-2020'
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(404)
			})
		})

		it('Validar Get no endpoint api/ano-analise-regularidade/{ano}/ com ano zero', () => {
			var ano = '0'
			cy.validar_anos_analise_regularidade(ano).then((response) => {
				expect(response.status).to.eq(404)
			})
		})
	})
})