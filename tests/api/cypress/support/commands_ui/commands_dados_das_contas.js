import Dados_das_contas_Localizadores from '../locators/dados_das_contas_locators'
import { select_dados_das_contas } from '../../fixtures/sql/sql_commands'
import { select_saldo_recursos_dados_das_contas } from '../../fixtures/sql/sql_commands'

const dados_das_contas_localizadores = new Dados_das_contas_Localizadores

Cypress.Commands.add('clicar_dados_das_contas', () => { 
  cy.get(dados_das_contas_localizadores.aba_dados_das_contas())
    .should('be.visible')
    .click()
    cy.wait(5000)
})

Cypress.Commands.add('validar_preenchimento_dados_das_contas', (campo) => {
  const seletores = {
    aba_dados_das_contas: dados_das_contas_localizadores.aba_dados_das_contas(),
    conta_1: dados_das_contas_localizadores.tbl_conta_1(),
    conta_2: dados_das_contas_localizadores.tbl_conta_2(),
    banco: dados_das_contas_localizadores.tbl_banco(),
    tipo_de_conta: dados_das_contas_localizadores.tbl_tipo_de_conta(),
    agencia: dados_das_contas_localizadores.tbl_agencia(),
    numero_conta: dados_das_contas_localizadores.tbl_numero_conta(),
    saldo: dados_das_contas_localizadores.tbl_saldo()
  }

  const seletor = seletores[campo]
  if (!seletor) {
    throw new Error(`Campo "${campo}" não está mapeado em validar_campos_preenchidos_das_contas`)
  }

  cy.get(seletor).then($el => {
    if ($el.is('input') || $el.is('textarea')) { 
      cy.wrap($el).invoke('val').should('not.be.empty')
    } else { 
      cy.wrap($el).invoke('text').should('not.be.empty')
    }
  })
})

Cypress.Commands.add('exportar_dados_das_contas_associacao', () => {   
  cy.get(dados_das_contas_localizadores.btn_exportar_dados_da_associacao())
    .first()
    .should('be.visible')  
    .and('not.be.disabled')
    .click()
})

Cypress.Commands.add('exportar_ficha_cadastral_dados_das_contas_associacao', () => {   
  cy.get(dados_das_contas_localizadores.btn_exportar_ficha_cadastral_associacao())
    .should('be.visible')  
    .and('not.be.disabled')
    .click()
})

Cypress.Commands.add('validar_exportar_dados_das_contas_associacao', () => {   

  cy.get(dados_das_contas_localizadores.btn_exportar_dados_da_associacao())
    .should('be.visible')

  cy.get(dados_das_contas_localizadores.btn_exportar_ficha_cadastral_associacao())
    .should('be.visible')    
})

Cypress.Commands.add('validar_dados_das_contas_associacao', (associacaoId) => {

  if (!associacaoId) {
    throw new Error('associacaoId não foi enviado')
  }

  const TIPOS_CONTA = {
    1: 'Conta Corrente',
    2: 'Cartão',
    3: 'Poupança',
    3882: 'Cheque'
  }

  cy.task(
    'postgreSQL:query',
    select_dados_das_contas(associacaoId)
  ).then((result) => {

    const dadosBanco = result.rows

    expect(dadosBanco).to.exist

    const seletores = {
      banco: dados_das_contas_localizadores.tbl_banco(),
      tipo_de_conta: dados_das_contas_localizadores.tbl_tipo_de_conta(),
      agencia: dados_das_contas_localizadores.tbl_agencia(),
      numero_conta: dados_das_contas_localizadores.tbl_numero_conta(),
    }

    cy.get(seletores.banco).each(($el, index) => {

      const conta = dadosBanco[index]

      const tipoContaDescricao = TIPOS_CONTA[conta.tipo_conta_id]

      cy.wrap($el)
        .should('have.value', conta.banco_nome)

      cy.get(seletores.tipo_de_conta)
        .eq(index)
        .should('have.value', tipoContaDescricao)

      cy.get(seletores.agencia)
        .eq(index)
        .should('have.value', conta.agencia)

      cy.get(seletores.numero_conta)
        .eq(index)
        .should('have.value', conta.numero_conta)

    })
  })
})

Cypress.Commands.add('validar_saldo_recursos_dados_das_contas', () => {

  const seletores = {
    banco: dados_das_contas_localizadores.tbl_banco(),
    agencia: dados_das_contas_localizadores.tbl_agencia(),
    numero_conta: dados_das_contas_localizadores.tbl_numero_conta()
  }

  const normalizarTexto = (valor) => {
    if (!valor) return ''
    return String(valor).trim()
  }

  const dados = {}

  // CONTA
  cy.get(seletores.numero_conta)
    .eq(0)
    .invoke('val')
    .then(valor => {
      dados.numero_conta = normalizarTexto(valor)
    })

  // BANCO
  cy.get(seletores.banco)
    .eq(0)
    .invoke('val')
    .then(valor => {
      dados.banco = normalizarTexto(valor)
    })

  // AGENCIA
  cy.get(seletores.agencia)
    .eq(0)
    .invoke('val')
    .then(valor => {
      dados.agencia = normalizarTexto(valor)
    })

  cy.then(() => {

    const query = select_saldo_recursos_dados_das_contas(dados)

    cy.task('postgreSQL:query', query).then((resultado) => {

      const rows = resultado.rows || []

      expect(
        rows,
        `Nenhum saldo encontrado para conta ${dados.numero_conta}`
      ).to.not.be.empty

      rows.forEach((row, index) => {
        expect(
          row.saldo_extrato,
          `Saldo ${index} para conta ${dados.numero_conta}`
        ).to.exist

        cy.log(`Conta: ${dados.numero_conta}`)
        cy.log(`Banco: ${dados.banco}`)
        cy.log(`Agência: ${dados.agencia}`)
        cy.log(`Saldo banco [${index}]: ${row.saldo_extrato}`)
      })
    })
  })
})

Cypress.Commands.add('alterar_dados_das_contas_associacao', () => {

  cy.wait('@getAssociacao').then(({ response }) => {

    const associacaoId = response?.body?.id

    expect(associacaoId, 'id da associação').to.exist

    cy.select_dados_das_contas_associacao({
      associacao_id: associacaoId
    }).then((row) => {

      expect(row, 'dados do banco').to.exist

      cy.get(dados_das_contas_localizadores.tbl_banco())
        .eq(0)
        .clear()
        .type(String(row.banco_nome))

      cy.get(dados_das_contas_localizadores.tbl_agencia())
        .eq(0)
        .clear()
        .type(String(row.agencia))

      cy.get(dados_das_contas_localizadores.tbl_numero_conta())
        .eq(0)
        .clear()
        .type(String(row.numero_conta))
    })
  })
})

Cypress.Commands.add('validar_salvar_dados_das_contas_associacao', () => {   

  cy.get(dados_das_contas_localizadores.btn_salvar_dados_das_contas_associacao())
    .should('be.visible')
    .click()

  cy.get(dados_das_contas_localizadores.msg_editar_dados_das_contas_associacao())
    .should('be.visible')
    .and('contain.text', 'A edição foi salva com sucesso!')  
})

Cypress.Commands.add('cancelar_edicao_dados_das_contas_associacao', () => {   
  cy.get(dados_das_contas_localizadores.btn_cancelar_edicao_dados_das_contas_associacao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cancelar_edicao_dados_das_contas_associacao', () => {   

  cy.get(dados_das_contas_localizadores.msg_editar_dados_das_contas_associacao())
    .should('not.exist')    
})

Cypress.Commands.add('solicitar_encerramento_dados_das_contas_associacao', (botao) => {

  const hoje = new Date()
  const dia = String(hoje.getDate()).padStart(2, '0')
  const mes = String(hoje.getMonth() + 1).padStart(2, '0')
  const ano = hoje.getFullYear()
  const dataAtual = `${dia}/${mes}/${ano}`

  switch (botao) {

    case 'solicita_encerramento':
      cy.get(
        dados_das_contas_localizadores.tbl_data_solicitacao_dados_das_contas_associacao())
        .first()
        .should('be.visible')
        .clear()
        .type(dataAtual)

      cy.get(
        dados_das_contas_localizadores.btn_solicita_encerramento_dados_das_contas_associacao())
        .should('be.visible')
        .click()

      cy.get(dados_das_contas_localizadores.mdl_confirmar_encerramento_dados_das_contas_associacao(), { timeout: 15000 })
        .should('be.visible')
      .within(() => {
      cy.get(dados_das_contas_localizadores.tbl_confirmar_encerramento_dados_das_contas_associacao())
        .should('be.visible')
        .click()
      })
    break

    case 'cancela_solicitacao':
      cy.get(
        dados_das_contas_localizadores.btn_cancela_solicitacao_dados_das_contas_associacao())
        .should('be.visible')
        .click()

      cy.get(
        dados_das_contas_localizadores.tbl_confirmar_encerramento_dados_das_contas_associacao())
        .should('be.visible')
        .click()
    break

    case 'cancelar_modal_solicitado':
      cy.get('body').then(($body) => {

        if (
          $body.find(
            dados_das_contas_localizadores.btn_solicita_encerramento_dados_das_contas_associacao()).length
        ) {

          cy.get(
            dados_das_contas_localizadores.btn_solicita_encerramento_dados_das_contas_associacao())
            .should('be.visible')
            .click()
        }

        else if (
          $body.find(
            dados_das_contas_localizadores.btn_cancela_solicitacao_dados_das_contas_associacao()).length
        ) {

          cy.get(
            dados_das_contas_localizadores.btn_cancela_solicitacao_dados_das_contas_associacao())
            .should('be.visible')
            .click()
        }

      })

      cy.get(
        dados_das_contas_localizadores.btn_cancelar_modal_solicitacao_dados_das_contas_associacao())
        .should('be.visible')
        .click()
    break

    default:
      throw new Error(`Botão ${botao} não mapeado`)
  }
})