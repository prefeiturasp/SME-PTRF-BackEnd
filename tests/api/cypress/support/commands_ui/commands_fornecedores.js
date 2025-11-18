import Fornecedores_Localizadores from '../locators/fornecedores_locators'

const fornecedores_Localizadores = new Fornecedores_Localizadores

Cypress.Commands.add('clicar_btn_fornecedores', (btn_fornecedores, nome_tabela_edicao) => {
	switch (btn_fornecedores) {
		case 'Adicionar fornecedor':
			cy.get(fornecedores_Localizadores.btn_adicionar_fornecedores()).click()
			break
		case 'Filtrar':
			cy.get(fornecedores_Localizadores.btn_fitrar_pesquisa()).click()
			break
		case 'Apagar':
			cy.get(fornecedores_Localizadores.btn_apagar_fornecedores()).click()
			break
		case 'Editar':
			cy.get(fornecedores_Localizadores.btn_editar_fornecedores()).click()
			break
		case 'Excluir':
			cy.get(fornecedores_Localizadores.btn_excluir_fornecedores()).click()
			break
		case 'Salvar':
			cy.get(fornecedores_Localizadores.btn_salvar_fornecedores()).click()
			break
		default:
			break
	}
})

Cypress.Commands.add('informar_dados_fornecedores', (nome_do_fornecedor, cpf_cnpj) => {
	cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor()).clear()
	nome_do_fornecedor ? cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor()).type(nome_do_fornecedor) : ''
	cy.get(fornecedores_Localizadores.txt_cpf_cnpj()).clear()
	cpf_cnpj ? cy.get(fornecedores_Localizadores.txt_cpf_cnpj()).type(cpf_cnpj) : ''
})

Cypress.Commands.add('informar_dados_fornecedores_pesquisa', (nome_do_fornecedor, cpf_cnpj) => {
	nome_do_fornecedor ? cy.get(fornecedores_Localizadores.txt_nome_do_fornecedor_pesquisa()).type(nome_do_fornecedor) : ''
	cpf_cnpj ? cy.get(fornecedores_Localizadores.txt_cpf_cnpj_pesquisa()).type(cpf_cnpj) : ''
})

Cypress.Commands.add('validar_resultado_da_consulta_fornecedores', (valores_consulta_nome_fornecedor, valores_consulta_cpf_cnpj) => {
	cy.get(fornecedores_Localizadores.tbl_resultados_nome_fornecedor()).should('be.visible').and('contain', valores_consulta_nome_fornecedor);
	cy.get(fornecedores_Localizadores.tbl_resultados_cpf_cnpj_fornecedor()).should('be.visible').and('contain', valores_consulta_cpf_cnpj);
})
