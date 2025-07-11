class Motivo_Pagamento_Antecipado_Localizadores {
	// tela Pesquisar motivo pagamento antecipado
	btn_adicionar_adicionar_motivo_pagamento_antecipado = () => { return '.pb-4 > .btn' }
	txt_filtrar_por_motivo_de_pagamento_antecipado = () => {return '[data-qa="campo-filtrar-por-motivo-motivo-pagamento-antecipado"]'}
	btn_filtrar_motivo_de_pagamento_antecipado = () => {return '[data-qa="botao-filtrar-motivo-pagamento-antecipado"]'}

	// tela Adicionar motivo pagamento antecipado
    txt_nome_motivo_pagamento_antecipado = () => { return '[data-qa="campo-motivo-motivo-pagamento-antecipado"]' }
	btn_salvar_motivo_pagamento_antecipado = () => { return '[data-qa="botao-submit-modal-motivo-pagamento-antecipado"]' }

	msg_cadastro_motivo_pagamento_antecipado = () => { return '.Toastify__toast-body' }
	msg_erro_modal_cadastro_motivo_pagamento_antecipado = () => { return '.modal-body' }

	// tela Edição motivo pagamento antecipado
	tbl_tabela_nome_edicao_motivo_pagamento_antecipado = (nome_tabela_edicao) => { return `tr:contains(${nome_tabela_edicao})` }
	btn_editar_motivo_pagamento_antecipado = () => { return '[data-qa="botao-editar-motivo-pagamento-antecipado"]' }
	btn_apagar_motivo_pagamento_antecipado = () => { return '[data-qa="botao-confirmar-apagar-motivo-pagamento-antecipado"]' }
	btn_excluir_motivo_pagamento_antecipado = () => { return '.modal-footer > .btn-danger' }
}

export default Motivo_Pagamento_Antecipado_Localizadores