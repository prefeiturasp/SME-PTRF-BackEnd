class Associacao_Localizadores {
	// tela associacao consulta
	tbl_nome_associacao = () => { return '#nome' }
	tbl_dre_associacao = () => { return '#dre' }
	tbl_ccm_associacao = () => { return '#ccm' }
	tbl_eol_associacao = () => { return '#codigo_eol' }
	tbl_cnpj_associacao = () => { return '#cnpj' }
	tbl_email_associacao = () => { return '#email' }	

	btn_exportar_dados_da_associacao = () => { return 'div.d-flex.justify-content-end.pb-3 > button:nth-child(1) > svg' }
	btn_exportar_ficha_cadastral_associacao = () => { return 'div.d-flex.justify-content-end.pb-3 > button:nth-child(3) > svg' }
	msg_exportar_dados_da_associacao = () => { return 'p.ml-n3.text-dark' }

	// tela associacao editar
	btn_salvar_dados_da_associacao = () => { return '.btn-success'}
	msg_editar_dados_da_associacao = () => { return ':nth-child(2) > :nth-child(2)'}
	msg_nome_editar_dados_da_associacao = () => { return '.span_erro' }
	btn_cancelar_edicao_da_associacao = () => { return '.btn-outline-success.mt-2'}
	btn_confirmar_cancelar_edicao_da_associacao = () => { return '.modal-footer > :nth-child(1)'}
}

export default Associacao_Localizadores