import Fornecedores_Localizadores from '../locators/fornecedores_locators'

const fornecedores_Localizadores = new Fornecedores_Localizadores

Cypress.Commands.add('clicar_btn_fornecedores', (btn_fornecedores, nome_tabela_edicao) => {
	switch (btn_fornecedores) {
		case 'Adicionar fornecedor':
			cy.get(fornecedores_Localizadores.btn_adicionar_fornecedores(), { timeout: 30000 }).should('be.visible').click()
			break
		case 'Filtrar':
			cy.get(fornecedores_Localizadores.btn_fitrar_pesquisa(), { timeout: 30000 }).should('be.visible').click()
			break
		case 'Apagar':
			cy.get(fornecedores_Localizadores.btn_apagar_fornecedores(), { timeout: 30000 }).should('be.visible').click()
			break
		case 'Editar':
				if (nome_tabela_edicao) {
					cy.contains(nome_tabela_edicao, { timeout: 30000 }).closest('tr').within(() => {
						cy.get(fornecedores_Localizadores.btn_editar_fornecedores()).click()
					})
				} else {
					cy.get(fornecedores_Localizadores.btn_editar_fornecedores(), { timeout: 30000 }).should('be.visible').click()
				}
				break
		case 'Excluir':
			cy.get(fornecedores_Localizadores.btn_excluir_fornecedores(), { timeout: 30000 }).should('be.visible').click()
			break
		case 'Salvar':
			cy.get(fornecedores_Localizadores.btn_salvar_fornecedores(), { timeout: 30000 }).should('be.visible').click()
			break
		default:
			break
	}
})

Cypress.Commands.add('informar_dados_fornecedores', (nome_do_fornecedor, cpf_cnpj) => {
	cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor(), { timeout: 30000 }).should('be.visible').clear()
	nome_do_fornecedor ? cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor()).type(nome_do_fornecedor) : ''
	cy.get(fornecedores_Localizadores.txt_cpf_cnpj(), { timeout: 30000 }).should('be.visible').clear()
	cpf_cnpj ? cy.get(fornecedores_Localizadores.txt_cpf_cnpj()).type(cpf_cnpj) : ''
})

Cypress.Commands.add('informar_dados_fornecedores_pesquisa', (nome_do_fornecedor, cpf_cnpj) => {
	cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor_pesquisa(), { timeout: 30000 })
		.should('be.visible')
	if (nome_do_fornecedor) {
		cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor_pesquisa())
			.clear()
			.type(nome_do_fornecedor)
	}

	cy.get(fornecedores_Localizadores.txt_cpf_cnpj_pesquisa(), { timeout: 30000 })
		.should('be.visible')
	if (cpf_cnpj) {
		cy.get(fornecedores_Localizadores.txt_cpf_cnpj_pesquisa())
			.clear()
			.type(cpf_cnpj)
	}
})

Cypress.Commands.add('validar_resultado_da_consulta_fornecedores', (valores_consulta_nome_fornecedor, valores_consulta_cpf_cnpj) => {
	cy.get(fornecedores_Localizadores.tbl_resultados_nome_fornecedor(), { timeout: 30000 })
		.should('be.visible')
		.and('contain', valores_consulta_nome_fornecedor);
	cy.get(fornecedores_Localizadores.tbl_resultados_cpf_cnpj_fornecedor(), { timeout: 30000 })
		.should('be.visible')
		.and('contain', valores_consulta_cpf_cnpj);
})
