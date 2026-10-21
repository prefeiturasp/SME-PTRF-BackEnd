import Login_PTRF_Localizadores from '../locators/login_locators'

const login_PTRF_Localizadores = new Login_PTRF_Localizadores

const preencherEEnviarLoginDre = (tentativasRestantes = 2) => {
	cy.get(login_PTRF_Localizadores.texto_usuario(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .and('have.value', '')
	  .type(Cypress.config('usuario_homol_dre'));
	cy.get(login_PTRF_Localizadores.texto_senha(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .and('have.value', '')
	  .type(Cypress.config('senha_homol'));
	cy.get(login_PTRF_Localizadores.botao_acessar(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .click();

	return cy.wait('@loginDre', { timeout: 30000 }).then(({ response }) => {
		const status = response?.statusCode;
		const erroTransitorio = [502, 503, 504].includes(status);

		if (erroTransitorio && tentativasRestantes > 0) {
			Cypress.log({
				name: 'login-DRE',
				message: `gateway ${status}; nova tentativa`,
			});
			return cy
				.wait(2000, { log: false })
				.then(() => preencherEEnviarLoginDre(tentativasRestantes - 1));
		}

		expect(status, 'status do login DRE').to.eq(200);
	});
}

const preencherEEnviarLoginSme = (tentativasRestantes = 2) => {
	cy.get(login_PTRF_Localizadores.texto_usuario(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .and('have.value', '')
	  .type(Cypress.config('usuario_homol_sme'));
	cy.get(login_PTRF_Localizadores.texto_senha(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .and('have.value', '')
	  .type(Cypress.config('senha_homol'));
	cy.get(login_PTRF_Localizadores.botao_acessar(), { timeout: 30000 })
	  .should('be.visible')
	  .and('not.be.disabled')
	  .click();

	return cy.wait('@loginSme', { timeout: 30000 }).then(({ response }) => {
		const status = response?.statusCode;
		const erroTransitorio = [502, 503, 504].includes(status);

		if (erroTransitorio && tentativasRestantes > 0) {
			Cypress.log({
				name: 'login-SME',
				message: `gateway ${status}; nova tentativa`,
			});
			return cy
				.wait(2000, { log: false })
				.then(() => preencherEEnviarLoginSme(tentativasRestantes - 1));
		}

		expect(status, 'status do login SME').to.eq(200);
	});
}

Cypress.Commands.add('login_PTRF', (device) => {
	cy.configurar_visualizacao(device)
})

Cypress.Commands.add('realizar_login', (perfil) => {
	switch (perfil) {
		case "SME":
			cy.session('login-SME', () => {
				cy.visit(Cypress.config('baseUrlPTRFHomol'));
				cy.location('pathname', { timeout: 30000 }).should('eq', '/login');
				cy.intercept('POST', '**/api/login').as('loginSme');
				cy.wait(1000, { log: false });
				preencherEEnviarLoginSme();
				cy.location('pathname', { timeout: 30000 }).should('eq', '/seleciona-recurso');
				cy.contains('Programa de Transferência de Recursos Financeiros - PTRF', {
					timeout: 30000,
				})
					.should('be.visible')
					.closest('.ant-card')
					.click();
				cy.location('pathname', { timeout: 30000 }).should('not.eq', '/seleciona-recurso');
			});

			cy.visit(Cypress.config('baseUrlPTRFHomol'));
			cy.location('pathname', { timeout: 30000 })
			  .should('not.eq', '/login')
			  .and('not.eq', '/seleciona-recurso');
			break;

		case "DRE":
			cy.session('login-DRE', () => {
				cy.visit(Cypress.config('baseUrlPTRFHomol'));
				cy.location('pathname', { timeout: 30000 }).should('eq', '/login');
				cy.intercept('POST', '**/api/login').as('loginDre');
				cy.wait(1000, { log: false });
				preencherEEnviarLoginDre();
				cy.location('pathname', { timeout: 30000 }).should('not.eq', '/login');
			});

			cy.visit(Cypress.config('baseUrlPTRFHomol'));
			cy.location('pathname', { timeout: 30000 }).should('not.eq', '/login');
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
