import Login_PTRF_Localizadores from '../locators/login_locators'

const login_PTRF_Localizadores = new Login_PTRF_Localizadores

Cypress.Commands.add('login_PTRF', (device) => {
	cy.configurar_visualizacao(device)
})

Cypress.Commands.add('realizar_login', (perfil) => {
	switch (perfil) {
		case "SME":
			cy.get(login_PTRF_Localizadores.texto_usuario()).type(Cypress.config('usuario_homol_sme'));
			cy.get(login_PTRF_Localizadores.texto_senha()).type(Cypress.config('senha_homol'));
			cy.get(login_PTRF_Localizadores.botao_acessar()).should('be.visible').click();
			break;
		case "DRE":
			cy.get(login_PTRF_Localizadores.texto_usuario()).type(Cypress.config('usuario_homol_dre'));
			cy.get(login_PTRF_Localizadores.texto_senha()).type(Cypress.config('senha_homol'));
			cy.get(login_PTRF_Localizadores.botao_acessar()).should('be.visible').click();
			break;
		default:
			console.error("Perfil não encontrado!");
	}

})