import Tipo_de_transacao_Localizadores from '../locators/tipo_de_transacao_locators'
import Commons_Locators from '../locators/commons_locators'

const commons_locators = new Commons_Locators
const tipo_de_transacao_Localizadores = new Tipo_de_transacao_Localizadores

Cypress.Commands.add('clicar_btn_adicionar_tipo_de_transacao', (btn_tipo_transacao, nome_tabela_edicao) => {
	switch (btn_tipo_transacao) {
		case 'Adicionar tipo de transacao':
			cy.get(tipo_de_transacao_Localizadores.btn_adicionar_tipo_de_transacao()).click()
			break
		case 'Salvar':
			cy.get(tipo_de_transacao_Localizadores.btn_salvar()).click()
			break
		case 'Filtrar':
			cy.get(tipo_de_transacao_Localizadores.btn_filtrar_tipo_de_transacao()).click()
			break
		case 'Editar':
			cy.get(commons_locators.tbl_nome_todas_consultas_edicao(nome_tabela_edicao)).find(tipo_de_transacao_Localizadores.btn_editar_tipo_transacao()).click()
			break
		case 'Apagar':
			cy.get(tipo_de_transacao_Localizadores.btn_apagar_tipo_transacao()).click()
			break
		case 'Excluir':
			cy.get(tipo_de_transacao_Localizadores.btn_excluir_tipo_transacao()).click()
			break
		default:
			break
	}
})

Cypress.Commands.add('informar_dados_tipo_de_transacao', (nome_tipo_de_transacao, tem_documento) => {
	cy.get(tipo_de_transacao_Localizadores.txt_nome()).clear()
	nome_tipo_de_transacao ? cy.get(tipo_de_transacao_Localizadores.txt_nome()).type(nome_tipo_de_transacao) : ''
	if (tem_documento === 'true') {
		cy.get(tipo_de_transacao_Localizadores.rdb_tem_documento_sim()).click()
	} else {
		cy.get(tipo_de_transacao_Localizadores.rdb_tem_documento_nao()).click()
	}
})

Cypress.Commands.add('informar_dados_filtro_por_nome_tipo_de_transacao', (filtrar_por_nome) => {
	cy.get(tipo_de_transacao_Localizadores.txt_filtrar_por_nome_tipo_de_transacao()).type(filtrar_por_nome)
})

