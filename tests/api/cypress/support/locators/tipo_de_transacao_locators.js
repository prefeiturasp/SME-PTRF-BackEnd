class Tipo_De_Transacao_Localizadores {
  // tela Pesquisar tipo de transacao
  btn_adicionar_tipo_de_transacao = () => {
    return ".pb-4 > .btn";
  };
  txt_filtrar_por_nome_tipo_de_transacao = () => {
    return "#filtrar_por_nome";
  };
  btn_filtrar_tipo_de_transacao = () => {
    return "form > .d-flex > .btn-success";
  };
  tbl_resultados_da_consulta = () => {
    return '[class="p-datatable-table"]';
  };

  // tela Adicionar tipo de transacao
  txt_nome = () => {
    return "#nome";
  };
  rdb_tem_documento_sim = () => {
    return '[data-qa="campo-tem-documento-true"]';
  };
  rdb_tem_documento_nao = () => {
    return '[data-qa="campo-tem-documento-false"]';
  };
  btn_salvar = () => {
    return ":nth-child(3) > .btn";
  };

  // tela Editar tipo transação

  btn_editar_tipo_transacao = () => {
    return ".btn-editar-membro";
  };
  btn_apagar_tipo_transacao = () => {
    return ".flex-grow-1 > .btn";
  };
  btn_excluir_tipo_transacao = () => {
    return ".modal-footer > .btn-danger";
  };
}

export default Tipo_De_Transacao_Localizadores;
