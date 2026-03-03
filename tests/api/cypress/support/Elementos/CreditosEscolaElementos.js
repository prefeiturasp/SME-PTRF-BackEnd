class CreditosEscolaElementos {
  //----------------------- Selecionar Tipos de Receita -------------------------\\
  arredondamento = () => {
    return cy
      .get(".d-flex > #tipo_receita", { timeout: 10000 }).should('be.visible')
      .select("Arredondamento na transferência de saldo entre cartões BB");
  };
  devolucaoConta = () => {
    return cy.get("#tipo_receita", { timeout: 10000 }).should('be.visible').select("Devolução à conta");
  };
  estorno = () => {
    return cy.get("#tipo_receita", { timeout: 10000 }).should('be.visible').select("Estorno");
  };
  recursoExterno = () => {
    return cy.get("#tipo_receita", { timeout: 10000 }).should('be.visible').select("Recurso Externo");
  };
  rendimento = () => {
    return cy.get("#tipo_receita", { timeout: 10000 }).should('be.visible').select("Rendimento");
  };
  repasse = () => {
    return cy.get("#tipo_receita", { timeout: 10000 }).should('be.visible').select("Repasse");
  };

  //----------------------- Botões -------------------------\\
  botaoFiltrarReceita = () => {
    return cy.get(".form-inline > .d-flex > .btn").contains("Filtrar");
  };
  botaoMaisFiltros = () => {
    return cy.get("button.btn.btn-outline-success").contains("Mais Filtros");
    

  };
  botaoFiltrarMaisFiltros = () => {
    return cy
      .get(":nth-child(1) > form > .d-flex > .btn-success")
      .contains("Filtrar");
  };
  botaoLimparFiltros = () => {
    return cy.get(".btn-outline-success.ml-2").contains("Limpar Filtros");
  };
  botaoCadastrarCredito = () => {
    return cy
      .get(".col-md-5.mt-2 > :nth-child(1)")
      .contains("Cadastrar crédito");
  };
  botaoValoresReprogramados = () => {
    return cy.get(".col-md-5.mt-2 > .mr-2").contains("Valores reprogramados");
  };
  botaoSalvarCadastroCredito = () => {
    return cy.get(".btn-success").contains("Salvar");
  };
  botaoCancelar = () => {
    return cy
      .get(":nth-child(1) > form > .d-flex > :nth-child(1)")
      .contains("Cancelar");
  };
  botaoDeletarCadastroCredito = () => {
    return cy.get(".btn-danger").contains("Deletar");
  };
  botaoVoltarCadastroCredito = () => {
    return cy.get(".btn-outline-success").contains("Voltar");
  };
  botaoNaoCancelarRepasse = () => {
    return cy.get(".modal-footer > .btn-outline-success");
  };
  botaoGravarRepasse = () => {
    return cy.get(".modal-footer > .btn-success");
  };

  //----------------------- Mais Filtros -------------------------\\
  arredondamentoMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Arredondamento na transferência de saldo entre cartões BB");
  };
  devolucaoContaMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Devolução à conta");
  };
  estornoMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Estorno");
  };
  recursoExternoMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Rendimento");
  };
  rendimentoMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Rendimento");
  };
  repasseMaisFiltros = () => {
    return cy
      .get(".form-row > :nth-child(1) > #tipo_receita")
      .select("Repasse");
  };
  selecionarDetalhamentoCreditoMaisFiltros = () => {
    return cy.get("#filtrar_por_termo");
  };

  //----------------------- Colunas dos Créditos Cadastrados -------------------------\\
  validarTipo = () => {
    return cy.get(".p-datatable-thead tr", { timeout: 10000 }).should('be.visible').contains("Tipo");
  };
  validarConta = () => {
    return cy.get(".p-datatable-thead tr", { timeout: 10000 }).should('be.visible').contains("Conta");
  };
  validarAcao = () => {
    return cy.get(".p-datatable-thead tr", { timeout: 10000 }).should('be.visible').contains("Ação");
  };
  validarData = () => {
    return cy.get(".p-datatable-thead tr", { timeout: 10000 }).should('be.visible').contains("Data");
  };
  validarValor = () => {
    return cy.get(".p-datatable-thead tr", { timeout: 10000 }).should('be.visible').contains("Valor");
  };

  //----------------------- Cadastro de Crédito -------------------------\\
  selecionarDetalhamentoCredito = () => {
    return cy.get("#detalhe_tipo_receita").select("Julho");
  };
  selecionarDataCredito = () => {
    return cy.get(".react-datepicker__input-container > .form-control");
  };

  selecionarDataCreditoCalendario = () => {
    return cy.get(".react-datepicker__month-container");
    
  };

  selecionarTipoContaCheque = () => {
    return cy.get("#conta_associacao").select("Cheque");
  };
  selecionarTipoContaCartao = () => {
    return cy.get("#conta_associacao").select("Cartão");
  };
  selecionarValorTotalCredito = () => {
    return cy.get("#valor");
  };

  //----------------------- Cadastro de Crédito (Ação) -------------------------\\
  selecionarAcaoPtrf = () => {
    return cy.get("#acao_associacao").select("PTRF Básico");
  };
  selecionarAcaoSalas = () => {
    return cy.get("#acao_associacao").select("Salas e Espaços de Leitura");
  };
  selecionarAcaoMaterialPedagogico = () => {
    return cy.get("#acao_associacao").select("Material Pedagógico");
  };
  selecionarAcaoRecurso = () => {
    return cy.get("#acao_associacao").select("Recurso Externo");
  };
  selecionarAcaoMaterialComplementar = () => {
    return cy.get("#acao_associacao").select("Material Complementar");
  };
  selecionarDataIncio = () => {
    return cy.get(
      ".pr-0 > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control"
    );
  };
  selecionarDataFim = () => {
    return cy.get(
      ".pl-0 > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control"
    );
  };

  //----------------------- Classificação do Crédito -------------------------\\
  selecionarClassificacaoCreditoCusteio = () => {
    return cy.get("#categoria_receita").select("Custeio");
  };
  selecionarClassificacaoCreditoLivreAplicacao = () => {
    return cy.get("#categoria_receita").select("Livre Aplicação");
  };

  //----------------------- Tipos do Crédito -------------------------\\
  selecionarReceitaRendimento = () => {
    return cy.get("#tipo_receita").select("Rendimento");
  };
  selecionarReceitaRepasse = () => {
    return cy.get("#tipo_receita").select("Repasse");
  };

  //----------------------- Grid Repasse -------------------------\\
  selecionarValorCapital = () => {
    return cy.contains("8.000,00");
  };
  selecionarValorCusteio = () => {
    return cy.contains("8.500,00");
  };
  selecionarValorLivreAplicacao = () => {
    return cy.contains("57.478,00");
  };

  //----------------------- Mensagens Campos Obrigatórios -------------------------\\
  validaDetalhamento = () => {
    return cy
      .get(":nth-child(2) > .span_erro")
      .contains("Detalhamento do crédito é obrigatório");
  };
  validaDataCredito = () => {
    return cy
      .get(":nth-child(3) > .span_erro")
      .contains("Data do crédito é obrigatório.");
  };
  validaTipoConta = () => {
    return cy
      .get(":nth-child(4) > .span_erro")
      .contains("Tipo de conta é obrigatório.");
  };
  validaAcaoSelecionada = () => {
    return cy.get(":nth-child(5) > .span_erro").contains("Ação é obrigatório.");
  };
  validaClassificacaoSelecionada = () => {
    return cy
      .get(":nth-child(6) > .span_erro")
      .contains("Classificação do crédito é obrigatório.");
  };
  validaCampoValor = () => {
    return cy
      .get(":nth-child(7) > .span_erro")
      .contains("Valor do crédito é obrigatório.");
  };

  //----------------------- Edição Cadastro de Crédito -------------------------\\
  editarRendimento = () => {
    return cy
      .get(".p-datatable-tbody > :nth-child(1) > :nth-child(1)")
      .contains("Rendimento");
  };
  editarRepasse = () => {
    return cy
      .get(".p-datatable-tbody > :nth-child(1) > :nth-child(1)")
      .contains("Repasse");
  };

  //----------------------- Validar Créditos da Escola -------------------------\\
  avancarPaginas = () => {
    return cy.get(".p-paginator-next");
  };
  validarTabelaValor = () => {
    return cy.get(".p-datatable-tbody tr");
  };
  recebeValor = () => {
    return cy.get("td.py-3").find("span");
  };
  validarValorTotalFiltroAplicado = () => {
    return cy.get(".table > tbody > tr > :nth-child(2)");
  };
  validarSemFiltroAplicado = () => {
    return cy.get(".table > thead > tr > :nth-child(1)");
  };

  validarSomaCreditos = () => {
    return cy.get(".mb-3");
  };


  //----------------------- Retorno de Mensagens apresentadas em tela -------------------------\\
  semResultado = () => {
    return cy
      .get(".texto-404")
      .contains(
        "Não encontramos resultados, verifique os filtros e tente novamente."
      );
  };
}

export default CreditosEscolaElementos;
