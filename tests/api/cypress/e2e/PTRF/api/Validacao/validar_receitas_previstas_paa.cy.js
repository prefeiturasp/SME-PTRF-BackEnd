/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {
  var usuario = Cypress.config('usuario_homol_sme')
  var senha = Cypress.config('senha_homol')

  before(() => {
    cy.autenticar_login(usuario, senha)
  })

  context('Casos de teste para a rota de Post api/receitas-previstas-paa/', () => {

    it('Validar Post com acao associacao invalida', () => {
      var body = {
        paa: '00000000-0000-0000-0000-000000000000',
        acao_associacao: '0916e416-260f-473b-bb20-9e3b309',
        previsao_valor_capital: '1',
        previsao_valor_custeio: '1',
        previsao_valor_livre: '1'
      }

      cy.cadastrar_receitas_previstas_paa(body).then((response) => {
        expect(response.status).to.eq(400)
        expect(response.body.acao_associacao[0]).to.eq(
          '“0916e416-260f-473b-bb20-9e3b309” is not a valid UUID.'
        )
      })
    })

    it('Validar Post com acao associacao em branco', () => {
      var body = {
        paa: '00000000-0000-0000-0000-000000000000',
        acao_associacao: null,
        previsao_valor_capital: '1',
        previsao_valor_custeio: '1',
        previsao_valor_livre: '1'
      }

      cy.cadastrar_receitas_previstas_paa(body).then((response) => {
        expect(response.status).to.eq(400)
        expect(response.body.acao_associacao[0]).to.eq('This field may not be null.')
      })
    })

    it('Validar Post com valores invalidos nos campos de valores', () => {
      var body = {
        paa: '00000000-0000-0000-0000-000000000000',
        acao_associacao: 'b66803ee-25b2-489e-876c-37aa2d5adb3b',
        previsao_valor_capital: 'treze',
        previsao_valor_custeio: 'treze',
        previsao_valor_livre: 'treze'
      }

      cy.cadastrar_receitas_previstas_paa(body).then((response) => {
        expect(response.status).to.eq(400)
        expect(response.body.previsao_valor_capital[0]).to.eq('A valid number is required.')
        expect(response.body.previsao_valor_custeio[0]).to.eq('A valid number is required.')
        expect(response.body.previsao_valor_livre[0]).to.eq('A valid number is required.')
      })
    })

    it('Validar Post com valores em branco nos campos de valores', () => {
      var body = {
        paa: '00000000-0000-0000-0000-000000000000',
        acao_associacao: 'b66803ee-25b2-489e-876c-37aa2d5adb3b',
        previsao_valor_capital: '',
        previsao_valor_custeio: '',
        previsao_valor_livre: ''
      }

      cy.cadastrar_receitas_previstas_paa(body).then((response) => {
        expect(response.status).to.eq(400)
      })
    })
  })

  context('Casos de teste para a rota de Get api/receitas-previstas-paa/', () => {

    it('Validar Get sem parametro', () => {
      cy.validar_receitas_previstas_paa('').then((response) => {
        expect(response.status).to.eq(200)
        expect(response.body.results).to.exist
      })
    })

    it('Validar Get com parametro acao_nome', () => {
      cy.validar_receitas_previstas_paa('?acao_nome=PTRF%20B%C3%A1sico').then((response) => {
        expect(response.status).to.eq(200)
        expect(response.body.results).to.exist
      })
    })

    it('Validar Get com parametro acao_uuid', () => {
      cy.validar_receitas_previstas_paa('?acao_uuid=bdcbc8ce-7bab-48b3-959a-f866c6644579').then((response) => {
        expect(response.status).to.eq(200)
        expect(response.body.results).to.exist
      })
    })

    it('Validar Get com filtros invalidos', () => {
      cy.validar_receitas_previstas_paa(
        '?acao_nome=dsad&acao_uuid=bdcbc8ce-7bab-48b3-959a-f866c6644579'
      ).then((response) => {
        expect(response.status).to.eq(200)
        expect(response.body.results).to.exist
      })
    })
  })

  context('Casos de teste para a rota de Get api/receitas-previstas-paa/{uuid}', () => {

    it('Validar Get por uuid com sucesso', () => {
      cy.validar_receitas_previstas_paa('').then((response) => {
        var uuid = response.body.results[0].uuid

        cy.validar_receitas_previstas_paa(uuid).then((response) => {
          expect(response.status).to.eq(200)
          expect(response.body.uuid).to.eq(uuid)
        })
      })
    })

    it('Validar Get por uuid invalido', () => {
      cy.validar_receitas_previstas_paa('f234e1d2-d894-4445-bdbd-e01fc4db2').then((response) => {
        expect(response.status).to.eq(404)
        expect(response.statusText).to.eq('Not Found')
      })
    })
  })

})
