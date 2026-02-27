class Dados_das_contas_Localizadores {
	// tela dados das contas consulta
	aba_dados_das_contas = () => { return 'a[href="/dados-das-contas-da-associacao"]' }
	tbl_conta_1 = () => { return '#dados-conta-id-0' }
	tbl_conta_2 = () => { return '#dados-conta-id-1' }
	tbl_banco = () => { return '#dados-conta-id-0 > div.row > div:nth-child(2) > div > input' }
	tbl_tipo_de_conta = () => { return ':nth-child(3) > .form-group > .form-control' }
	tbl_agencia = () => { return 'div:nth-child(4) > div > input' }
	tbl_numero_conta = () => { return 'div:nth-child(5) > div > input' }
	tbl_saldo = () => { return '.saldo-recursos-conta' }	

	btn_exportar_dados_da_associacao = () => { return 'div > button:nth-child(1) > svg' }
	btn_exportar_ficha_cadastral_associacao = () => { return 'div > button:nth-child(3) > svg' }
	
	// tela dados das contas editar
	msg_editar_dados_das_contas_associacao = () => { return 'div:nth-child(2) > p:nth-child(2)'}	
	btn_cancelar_edicao_dados_das_contas_associacao = () => { return 'button.btn.btn.btn-outline-success.mt-2.mr-2'}
	btn_salvar_dados_das_contas_associacao = () => { return 'button.btn.btn-success.mt-2'}
	btn_solicita_encerramento_dados_das_contas_associacao = () => { return '#dados-conta-id-0 > .card > .card-body > .row > .col-6 > .mb-3 > .btn'}
	btn_cancela_solicitacao_dados_das_contas_associacao = () => { return '#dados-conta-id-0 button'}
	btn_cancelar_modal_solicitacao_dados_das_contas_associacao = () => { return '[data-qa="modal-confirmar-cancelar-solicitacao-btn-Cancelar"]'}
	tbl_data_solicitacao_dados_das_contas_associacao = () => { return 'input[name="data_extrato"]'}
	tbl_confirmar_encerramento_dados_das_contas_associacao = () => { return 'button:contains("Confirmar")' }
	mdl_confirmar_encerramento_dados_das_contas_associacao = () => { return '.modal.show'}
}

export default Dados_das_contas_Localizadores