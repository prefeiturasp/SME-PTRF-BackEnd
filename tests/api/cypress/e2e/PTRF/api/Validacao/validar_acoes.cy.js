/// <reference types='cypress' />

describe('Validar rotas de acoes da aplicação SigEscola', () => {

  var usuario = Cypress.config('usuario_homol_sme')
  var senha = Cypress.config('senha_homol')

  before(() => {
    cy.autenticar_login(usuario, senha)
  })

  context('Casos de teste para a rota GET api/acoes/', () => {

    it('Validar retorno do endpoint api/acoes com sucesso', () => {
      var id = ''
      cy.validar_acoes(id).then((response) => {
        expect(response.status).to.eq(200)
        expect(response.statusText).to.eq('OK')
      })
    })

  })

  context('Casos de teste para a rota GET api/acoes/{uuid}/', () => {

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

  context('Casos de teste para POST api/acoes/', () => {

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
        expect(response.body.posicao_nas_pesquisas[0])
          .to.eq('Ensure this field has no more than 10 characters.')
      })
    })

    it('Validar post no endpoint api/acoes com campos booleanos em branco', () => {
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

  context('Casos de teste para DELETE api/acoes/', () => {

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
        expect(response.body.detail).to.eq('Method "DELETE" not allowed.')
        expect(response.statusText).to.eq("Method Not Allowed")
      })
    })

  })

  context('Casos de teste para GET api/acoes/{uuid}/associacoes-nao-vinculadas/', () => {

    it('Validar retorno com uuid invalido', () => {
      var id = 'fd5f4'
      cy.validar_acoes_com_associacoes_nao_vinculadas(id).then((response) => {
        expect(response.status).to.eq(404)
        expect(response.statusText).to.eq('Not Found')
      })
    })

  })

  context('Casos de teste para GET api/acoes/{uuid}/associacoes-nao-vinculadas-por-nome/{nome}/', () => {

    it('Validar retorno com nome com vinculo', () => {
      var id = ''
      cy.validar_acoes(id).then((responseTodasAcoes) => {
        id = responseTodasAcoes.body[0].uuid
        var nome = responseTodasAcoes.body[0].nome

        cy.validar_acoes_com_associacoes_nao_vinculadas_por_nome(id, nome)
          .then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.exist
          })
      })
    })

    it('Validar retorno com sucesso filtrando por nome', () => {
      var id = ''
      cy.validar_acoes(id).then((responseTodasAcoes) => {
        id = responseTodasAcoes.body[0].uuid
        var nome = 'te'

        cy.validar_acoes_com_associacoes_nao_vinculadas_por_nome(id, nome)
          .then((response) => {
            expect(response.status).to.eq(200)
            expect(response.body).to.exist
          })
      })
    })

  })

})
