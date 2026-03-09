import Resumo_dos_recursos_Localizadores from '../locators/resumo_dos_recursos_locators'

const resumo_dos_recursos_localizadores = new Resumo_dos_recursos_Localizadores

Cypress.Commands.add('clicar_resumo_dos_recursos', () => { 
  cy.get(resumo_dos_recursos_localizadores.aba_resumo_dos_recursos())
    .should('be.visible')
    .click()
    cy.wait(5000)
})

Cypress.Commands.add('selecionar_periodo_resumo_dos_recursos', (campo) => { 
  let indice;

  if (campo === 'atual') {
    indice = 0
  } else if (campo === 'anterior') {
    indice = 1
  } else if (campo === 'penultimo') {
    indice = 2
  } else {
    throw new Error(`Campo inválido: ${campo}`)
  }

  cy.get(resumo_dos_recursos_localizadores.flt_periodo_resumo_dos_recursos())
    .should('be.visible')
    .find('option')
    .eq(indice)
    .then(option => {
      cy.get(resumo_dos_recursos_localizadores.flt_periodo_resumo_dos_recursos())
        .select(option.val());
  })
})

Cypress.Commands.add('selecionar_conta_resumo_dos_recursos', (campo) => { 
  let indice;

  if (campo === 'todas') {
    indice = 0
  } else if (campo === 'cheque') {
    indice = 1
  } else if (campo === 'cartao') {
    indice = 2
  } else {
    throw new Error(`Campo inválido: ${campo}`)
  }

  cy.get(resumo_dos_recursos_localizadores.flt_conta_resumo_dos_recursos())
    .should('be.visible')
    .find('option')
    .eq(indice)
    .then(option => {
      cy.get(resumo_dos_recursos_localizadores.flt_conta_resumo_dos_recursos())
        .select(option.val());
  })
})

Cypress.Commands.add('validar_filtro_resumo_dos_recursos', () => { 
  cy.get(resumo_dos_recursos_localizadores.tbl_periodo_resumo_dos_recursos())
    .should('be.visible')
})

Cypress.Commands.add('validar_card_resumo_dos_recursos', (card) => {
  cy.get(resumo_dos_recursos_localizadores.cards_resumo_dos_recursos())
    .should('be.visible')
    .contains(card)
    .should('exist')
})

Cypress.Commands.add('validar_saldo_resumo_dos_recursos', () => {
  cy.get(resumo_dos_recursos_localizadores.cards_saldos_resumo_dos_recursos())
    .should('be.visible')
})

Cypress.Commands.add('verficar_saldo_reprogramado_resumo_dos_recursos', () => {

  const totais = []

  // pega todos os valores do card TOTAL
  cy.get(resumo_dos_recursos_localizadores.cards_saldos_resumo_dos_recursos())
    .each(($el) => {
      const texto = $el.text()
      const valor = texto.replace('Total:', '').trim()
      totais.push(valor)
    })

  // pega todos os saldos reprogramados
  cy.get('.pt-1.mb-4 strong').each(($el) => {

    const saldo = $el.text().trim()

    // valida se existe algum total igual
    expect(totais).to.include(saldo)

  })

})