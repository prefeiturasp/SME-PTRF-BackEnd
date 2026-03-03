class Tipo_de_conta_Localizadores {
  // tela tipos de conta
  btn_adicionar_tipo_de_conta = () => {
    return '[class="btn btn-base-verde mt-2"]';
  };
  tbl_resultados_da_consulta = () => {
    return '[class="p-datatable-table"]';
  };

  resultado_pesquisa_tipo_conta = () => {
    return "p";
  };
  txt_pesquisar = () => {
    return "#filtro-nome";
  };
  btn_pesquisar = () => {
    return ".btn-pesquisar-tipos-conta";
  };

  // tela adicionar tipo de conta
  txt_nome_do_tipo_de_conta = () => {
    return "#nome";
  };
  txt_nome_do_banco = () => {
    return "#banco_nome";
  };
  txt_n_da_agencia = () => {
    return "#agencia";
  };
  txt_n_da_conta = () => {
    return "#numero_conta";
  };
  txt_n_do_cartao = () => {
    return "#numero_cartao";
  };

  chk_exibir_os_dados_da_conta_somente_leitura = () => {
    return "#apenas_leitura";
  };
  chk_conta_permite_encerramento = () => {
    return "#permite_inativacao";
  };

  btn_cancelar = () => {
    return ":nth-child(2) > .btn";
  };
  btn_salvar = () => {
    return ":nth-child(3) > .btn";
  };

  // edicao tipo conta
  btn_editar = () => {
    return "tbody > tr:nth-child(1) > td:nth-child(2) > button > span";
  };

  // edicao tipo conta
  btn_apagar_tipo_conta = () => {
    return ".flex-grow-1 > .btn";
  };
  btn_excluir = () => {
    return ".modal-footer > .btn-base-vermelho";
  };
}

export default Tipo_de_conta_Localizadores;
