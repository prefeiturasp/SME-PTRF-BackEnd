import Login_PTRF_Localizadores from '../locators/login_locators'

const login_PTRF_Localizadores = new Login_PTRF_Localizadores

Cypress.Commands.add('login_PTRF', (device) => {
	cy.configurar_visualizacao(device)
})

Cypress.Commands.add('realizar_login', (perfil) => {
	switch (perfil) {
		case "SME":
			cy.get(login_PTRF_Localizadores.texto_usuario())
			  .type(Cypress.config('usuario_homol_sme'));
			cy.get(login_PTRF_Localizadores.texto_senha())
			  .type(Cypress.config('senha_homol'));
			cy.get(login_PTRF_Localizadores.botao_acessar())
			  .should('be.visible').click();

			// espera 10 segundos após o login e, se o card aparecer, clicar para fechar
			cy.wait(10000)
			const condicaoSelector = ':nth-child(2) > .ant-spin-nested-loading > .ant-spin-container > .ant-card > .ant-card-body > .ant-typography'
			const cliqueSelector = ':nth-child(2) > .ant-spin-nested-loading > .ant-spin-container > .ant-card > .ant-card-body > div'

			cy.get('body').then($body => {
				if ($body.find(condicaoSelector).length) {
					cy.get(cliqueSelector).click({ force: true })
				}
			})
			break;

		case "DRE":
			cy.get(login_PTRF_Localizadores.texto_usuario())
			  .type(Cypress.config('usuario_homol_dre'));
			cy.get(login_PTRF_Localizadores.texto_senha())
			  .type(Cypress.config('senha_homol'));
			cy.get(login_PTRF_Localizadores.botao_acessar())
			  .should('be.visible').click();
			break;

		case "UE":
			cy.get(login_PTRF_Localizadores.texto_usuario())
			  .type(Cypress.config('usuario_homol_ue'));
			cy.get(login_PTRF_Localizadores.texto_senha())
			  .type(Cypress.config('senha_teste'));
			cy.get(login_PTRF_Localizadores.botao_acessar())
			  .should('be.visible').click();
			break;

		default:
			console.error("Perfil não encontrado!");
	}
})