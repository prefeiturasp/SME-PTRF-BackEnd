import Motivo_Pagamento_Antecipado_Localizadores from '../locators/motivo_pagamento_antecipado_locators'

const motivo_pagamento_antecipado_Localizadores = new Motivo_Pagamento_Antecipado_Localizadores

Cypress.Commands.add('clicar_btn_motivo_pagamento_antecipado', (btn_motivo_pagamento_antecipado, nome_tabela_edicao) => {
	switch (btn_motivo_pagamento_antecipado) {
		case 'Adicionar motivo de pagamento antecipado':
			cy.get(motivo_pagamento_antecipado_Localizadores.btn_adicionar_adicionar_motivo_pagamento_antecipado()).click()
			break
		case 'Salvar':
			cy.get(motivo_pagamento_antecipado_Localizadores.btn_salvar_motivo_pagamento_antecipado()).click()
			break
		case 'Filtrar':
			cy.get(motivo_pagamento_antecipado_Localizadores.btn_filtrar_motivo_de_pagamento_antecipado()).click()
			break
		case 'Editar':
			cy.get(motivo_pagamento_antecipado_Localizadores.tbl_tabela_nome_edicao_motivo_pagamento_antecipado(nome_tabela_edicao)).find(motivo_pagamento_antecipado_Localizadores.btn_editar_motivo_pagamento_antecipado()).click()
			break
		case 'Apagar':
			cy.get(motivo_pagamento_antecipado_Localizadores.btn_apagar_motivo_pagamento_antecipado()).click()
			break
		case 'Excluir':
			cy.get(motivo_pagamento_antecipado_Localizadores.btn_excluir_motivo_pagamento_antecipado()).click()
			break
		default:
			break
	}
})

Cypress.Commands.add('informar_dados_motivo_pagamento_antecipado', (nome_do_motivo_pagamento_antecipado) => {
	cy.get(motivo_pagamento_antecipado_Localizadores.txt_nome_motivo_pagamento_antecipado()).clear()
	nome_do_motivo_pagamento_antecipado ? cy.get(motivo_pagamento_antecipado_Localizadores.txt_nome_motivo_pagamento_antecipado()).type(nome_do_motivo_pagamento_antecipado) : ''
})

Cypress.Commands.add('informar_dados_pesquisa_motivo_pagamento_antecipado', (nome_do_motivo_pagamento_antecipado) => {
	cy.get(motivo_pagamento_antecipado_Localizadores.txt_filtrar_por_motivo_de_pagamento_antecipado()).clear()
	nome_do_motivo_pagamento_antecipado ? cy.get(motivo_pagamento_antecipado_Localizadores.txt_filtrar_por_motivo_de_pagamento_antecipado()).type(nome_do_motivo_pagamento_antecipado) : ''
})
