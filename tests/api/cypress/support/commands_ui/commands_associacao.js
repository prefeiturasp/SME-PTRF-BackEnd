import Associacao_Localizadores from '../locators/associacao_locators'

const associacao_Localizadores = new Associacao_Localizadores

Cypress.Commands.add('validar_dados_da_associacao', (campo, valorEsperado) => {

  const seletores = {
    nome_associacao: '#nome',
    dre: '#dre',
    ccm: '#ccm',
    codigo_eol: '#codigo_eol',
    cnpj: '#cnpj',
    email: '#email'
  }

  const seletor = seletores[campo]
  if (!seletor) {
    throw new Error(`Campo "${campo}" não está mapeado em validar_associacao`)
  }
  
  cy.get(seletor).then($el => {
    if ($el.is('input') || $el.is('textarea')) {
      cy.wrap($el).should('have.value', valorEsperado)
    } else {
      cy.wrap($el).should('have.text', valorEsperado)
    }
  })
})

Cypress.Commands.add('exportar_dados_da_associacao', () => {   
  cy.get(associacao_Localizadores.btn_exportar_dados_da_associacao())
    .should('be.visible')  
    .and('not.be.disabled')
    .click()
})

Cypress.Commands.add('exportar_ficha_cadastral_associacao', () => {   
  cy.get(associacao_Localizadores.btn_exportar_ficha_cadastral_associacao())
    .should('be.visible')  
    .and('not.be.disabled')
    .click()
})

Cypress.Commands.add('validar_exportar_dados_da_associacao', () => {   
  cy.get(associacao_Localizadores.msg_exportar_dados_da_associacao())
    .should('be.visible')

  cy.get(associacao_Localizadores.btn_exportar_dados_da_associacao())
    .should('be.visible')

  cy.get(associacao_Localizadores.btn_exportar_ficha_cadastral_associacao())
    .should('be.visible')    
})

Cypress.Commands.add('informar_dados_da_associacao', (nome_associacao, ccm) => {

  function preencherCampo(seletor, valor) {
    cy.get(seletor)
      .should('be.visible')
      .clear()

    if (valor) {
      cy.get(seletor).type(valor)
    }
  }

  preencherCampo(
    associacao_Localizadores.tbl_nome_associacao(),
    nome_associacao
  )

  preencherCampo(
    associacao_Localizadores.tbl_ccm_associacao(),
    ccm
  )
})

Cypress.Commands.add('salvar_dados_da_associacao', () => {   
  cy.get(associacao_Localizadores.btn_salvar_dados_da_associacao())
    .should('be.visible')
    .and('not.be.disabled')
    .click()
})

Cypress.Commands.add('validar_editar_dados_da_associacao', (mensagem) => {   
  cy.get(associacao_Localizadores.msg_editar_dados_da_associacao())
    .should('be.visible')
    .and('contain.text', mensagem)
})

Cypress.Commands.add('validar_nome_editar_dados_da_associacao', (alerta) => {   
  cy.get(associacao_Localizadores.msg_nome_editar_dados_da_associacao())
    .should('be.visible')
    .and('contain.text', alerta)
})

Cypress.Commands.add('validar_campos_bloqueados', () => {

  const seletores = [
    '#dre',
    '#ccm',
    '#codigo_eol',
    '#email'
  ]

  seletores.forEach(seletor => {

    cy.get(seletor)
      .should('be.visible')
      .and(($input) => {
        expect(
          $input.prop('disabled') || $input.prop('readOnly'),
          `Campo ${seletor} deve estar bloqueado`
        ).to.be.true
      })
  })
})

Cypress.Commands.add('cancelar_edicao_da_associacao', () => {
  cy.get(associacao_Localizadores.btn_cancelar_edicao_da_associacao())
    .should('be.visible')
    .click()

  cy.get(associacao_Localizadores.btn_confirmar_cancelar_edicao_da_associacao())
    .should('be.visible')
    .click()
})

Cypress.Commands.add('validar_cancelar_edicao_da_associacao', () => {
  cy.get(associacao_Localizadores.btn_cancelar_edicao_da_associacao())
    .should('be.visible')
})