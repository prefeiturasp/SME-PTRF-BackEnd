class Tipo_de_conta_Localizadores {
	// tela fornecedores pesquisa
	btn_adicionar_fornecedores = () => { return '.pb-4 > .btn' }
	tbl_resultados_nome_fornecedor = () => { return '.p-datatable-tbody > :nth-child(1) > :nth-child(1)' }
	tbl_resultados_cpf_cnpj_fornecedor = () => { return '.p-datatable-tbody > :nth-child(1) > :nth-child(2)' }

	txt_nome_do_fornecedor_pesquisa = () => { return '#filtrar_por_nome' }
	txt_cpf_cnpj_pesquisa = () => { return '#filtrar_por_cpf_cnpj' }

	btn_fitrar_pesquisa = () => { return 'form > .d-flex > .btn-success' }
	btn_limpar_pesquisa = () => { return '.btn-outline-success' }

	// tela cadastro fornecedores 
	txt_nome_do_fornecedor = () => { return '#nome' }
	txt_cpf_cnpj = () => { return '#cpf_cnpj' }

	msg_cadastro_fornecedores = () => { return '.Toastify__toast-body' }
	msg_erro_modal_cadastro_fornecedores = () => { return '.modal-body' }

	// edicao tipo conta
	tbl_tabela_nome_edicao_fornecedores = (nome_tabela_edicao) => { return `tr:contains(${nome_tabela_edicao})` }
	btn_editar_fornecedores = () => { return '.btn-editar-membro' }

	// edicao fornecedor
	btn_apagar_fornecedores = () => { return '.flex-grow-1 > .btn' }
	btn_excluir_fornecedores = () => { return '.modal-footer > .btn-danger' }
	btn_salvar_fornecedores = () => { return ':nth-child(3) > .btn'}


}

export default Tipo_de_conta_Localizadores