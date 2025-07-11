import Painel_Parametrizacao_Localizadores from '../locators/painel_parametrizacao_locators'

const painel_Parametrizacao_Localizadores = new Painel_Parametrizacao_Localizadores

Cypress.Commands.add('clicar_opcao_painel_parametrizacao', (opcao_painel_parametrizacao) => {
	cy.contains(painel_Parametrizacao_Localizadores.opcao_painel_parametrizacao(opcao_painel_parametrizacao)).click()
})

Cypress.Commands.add('clicar_opcao_menu_sme', (opcao_menu) => {
	cy.get(painel_Parametrizacao_Localizadores.opcao_menu()).contains(opcao_menu).click({force: true})
})