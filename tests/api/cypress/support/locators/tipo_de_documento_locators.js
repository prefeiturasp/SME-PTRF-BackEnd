class Tipo_De_Documento_Localizadores {
	// tela Adicionar tipo de documento
	txt_nome_tipo_de_documento = () => { return '[data-qa="campo-nome-tipo-documento"]' }
	rdb_solicitar_a_digitacao_do_numero_do_documento_sim = () => { return '[data-qa="campo-numero-documento-digitado-true"]' }
	rdb_solicitar_a_digitacao_do_numero_do_documento_nao = () => { return '[data-qa="campo-numero-documento-digitado-false"]' }
	rdb_no_numero_do_documento_deve_constar_apenas_digitos_sim = () => { return '[data-qa="campo-apenas-digitos-true"]' }
	rdb_no_numero_do_documento_deve_constar_apenas_digitos_nao = () => { return '[data-qa="campo-apenas-digitos-false"]' }
	rdb_documento_comprobatorio_de_despesa_sim = () => { return '[data-qa="campo-documento-comprobatorio-de-despesa-true"]' }
	rdb_documento_comprobatorio_de_despesa_nao = () => { return '[data-qa="campo-documento-comprobatorio-de-despesa-false"]' }
	rdb_habilita_preenchimento_do_imposto_sim = () => { return '[data-qa="campo-pode-reter-imposto-true"]' }
	rdb_habilita_preenchimento_do_imposto_nao = () => { return '[data-qa="campo-pode-reter-imposto-false"]' }
	rdb_documento_relativo_ao_imposto_recolhido_sim = () => { return '[data-qa="campo-documento-de-retencao-de-imposto-true"]' }
	rdb_documento_relativo_ao_imposto_recolhido_nao = () => { return '[data-qa="campo-documento-de-retencao-de-imposto-false"]' }
	btn_salvar_tipo_de_documento = () => { return '[data-qa="botao-submit-modal-tipo-documento"]' }

	// tela Pesquisa tipo de documento
	txt_filtrar_por_nome_tipo_de_documento = () => { return '[data-qa="campo-filtrar-por-nome-tipo-documento"]' }
	btn_filtrar_tipo_de_documento = () => { return '[data-qa="botao-filtrar-tipo-documento"]' }

	// tela Edição tipo documento
	btn_editar_tipo_documento = () => { return '[data-qa="botao-editar-tipo-documento"]' }

	// tela exclusao tipo documento
	btn_excluir_tipo_documento = () => { return '[data-qa="botao-confirmar-apagar-tipo-documento"]' }
	btn_confirmacao_excluir_tipo_documento = () => { return '.ant-btn-primary' }
}

export default Tipo_De_Documento_Localizadores 
