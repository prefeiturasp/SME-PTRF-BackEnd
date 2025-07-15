class GastosEscolaElementos {


    //----------------------- Botões -------------------------\\

    botaoFiltarTelaPrincipal = () => { return cy.get('.form-inline > .d-flex > .btn').contains('Filtrar')};    
    botaoMaisFiltros = () => { return cy.get('.pl-sm-0 > .btn').contains('Mais Filtros')};
    botaoCadastrarDespesa = () => { return cy.get('[data-qa="btn-cadastrar-despesa"]').contains('Cadastrar despesa')};
    botaoFiltrar = () => { return cy.get('[data-qa="btn-filtrar-filtro-avancado"]')};
    botaoLimparFiltros = () => { return cy.get('.btn-outline-success.ml-2').contains('Limpar Filtros')};
    botaoEstouCiente = () => { return cy.get('[data-qa="modal-despesa-aviso-capital-btn-Estou Ciente"]')};
    botaoAdicionarDespesaParcial = () => { return cy.get('[data-qa="cadastro-edicao-despesa-btn-adicionar-despesa-parcial"]').contains('+ Adicionar despesa parcial')};
    botaoCancelar = () => { return cy.get(':nth-child(1) > form > .d-flex > :nth-child(1)').contains('Cancelar')};
    botaoVoltar = () => { return cy.get('.pb-3 > .btn-outline-success').contains('Voltar')};
    botaoVoltarCadastroDespesa = () => { return cy.get('[data-qa="cadastro-edicao-despesa-btn-voltar"]').contains('Voltar')};
    botaoDeletar = () => { return cy.get('.btn-danger').contains('Deletar')};
    botaoSalvar = () => { return cy.get('.btn-success').contains('Salvar')};
    botaoSalvarCadastroDespesa = () => { return cy.get('[data-qa="cadastro-edicao-despesa-btn-salvar"]').contains('Salvar')};
    botaoModalTipoAplicacaoSim = () => { return cy.get('[data-qa="modal-tipo-recurso-nao-aceito-btn-Sim"]')};
    botaoModalTipoAplicacaoNao = () => { return cy.get('[data-qa="modal-tipo-recurso-nao-aceito-btn-Não"]')};
    botaoModalDespesaSim = () => { return cy.get('[data-qa="modal-despesa-incompleta-btn-Sim"]')};
    botaoModalDespesaNao = () => { return cy.get('[data-qa="modal-despesa-incompleta-btn-Não"]')}; 
    botaoDespesaCastradaSim = () => { return cy.get('[data-qa="modal-checar-despesa-existente-btn-Sim, salvar"]')};
    botaoSaldoInsuficienteOk = () => { return cy.get('[data-qa="modal-saldo-insuficiente-btn-OK"]')};
    botaoModalCancelarCadastroOk = () => { return cy.get('[data-qa="modal-despesa-cancelar-cadastro-btn-OK"]')};
    botaoModalCancelarCadastroFechar = () => { return cy.get('[data-qa="modal-despesa-cancelar-cadastro-btn-Fechar"]')};      
    botaoFechar = () => { return cy.get('.modal-footer > .btn').contains('Fechar')};


    //----------------------- Tela Mais Filtros -------------------------\\
    especificacaoMaisFiltros = () => { return cy.get('.form-row > :nth-child(1) > #filtrar_por_termo')};

    aplicacaoCapitalMaisFiltros = () => { return cy.get('#aplicacao_recurso_form_filtros_avancados_despesas').select("Capital")};
    aplicacaoCusteioMaisFiltros = () => { return cy.get('#aplicacao_recurso_form_filtros_avancados_despesas').select("Custeio")};

    acaoPtrfMaisFiltros = () => { return cy.get('#acao_associacao_form_filtros_avancados_despesas').select("PTRF Básico")};
    acaoSalasMaisFiltros = () => { return cy.get('#acao_associacao_form_filtros_avancados_despesas').select("Salas e Espaços de Leitura")};
    acaoMaterialPedagogicoMaisFiltros = () => { return cy.get('#acao_associacao_form_filtros_avancados_despesas').select("Material Pedagógico")};
    acaoRecursoMaisFiltros = () => { return cy.get('#acao_associacao_form_filtros_avancados_despesas').select("Recurso Externo")};
    acaoMaterialComplementarMaisFiltros = () => { return cy.get('#acao_associacao_form_filtros_avancados_despesas').select("Material Complementar")};

    informacacaoMaisFiltros = () => { return cy.get(':nth-child(4) > .ant-select > .ant-select-selector > .ant-select-selection-overflow')};
    informacacaoAntecipadoMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Antecipado"]')};
    informacacaoEstornadoMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Estornado"]')};
    informacacaoParcialMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Parcial"]')};
    informacacaoImpostoMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Imposto"]')};
    informacacaoImpostoPagoMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Imposto Pago"]')};
    informacacaoExcluidoMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Excluído"]')};
    informacacaoNaoReconhecidaMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Não Reconhecida"]')};
    informacacaoSemComprovacaoFiscalMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Sem comprovação fiscal"]')};
    informacacaoConciliadaMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Conciliada"]')};
    informacacaoNaoConciliadaMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Não conciliada"]')};

    contaChequeMaisFiltros = () => { return cy.get('#conta_associacao').select("Cheque")};
    contaCartaoMaisFiltros = () => { return cy.get('#conta_associacao').select("Cartão")};

    statusCompletoMaisFiltros = () => { return cy.get('#despesa_status').select("COMPLETO")};
    statusRascunhoMaisFiltros = () => { return cy.get('#despesa_status').select("RASCUNHO")};
    
    atividadeMaisFiltros = () => { return cy.get(':nth-child(7) > .ant-select > .ant-select-selector > .ant-select-selection-overflow')};
    atividadeCovidMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="COVID-19"]')};
    atividadeProgramaMaisFiltros = () => { return cy.get('.ant-select-dropdown').find('[title="Programa de Cuidados com as Estudantes"]')};

    fornecedorMaisFiltros = () => { return cy.get('#fornecedor')};

    periodoMaisFiltros = () => { return cy.get('.pr-0 > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control')};
    calendarioMaisFiltros = () => { return cy.get('.react-datepicker__month-container')};
    dataInicioPeriodoMaisFiltros = () => { return cy.get('input[name="data_inicio"]')};
    dataFimPeriodoMaisFiltros = () => { return cy.get('input[name="data_fim"]')};



    //----------------------- Grid Mais Filtros -------------------------\\
    resultadoGridMaisFiltos = () => { return cy.get('#tabela-lista-despesas > :nth-child(2) > :nth-child(1) > :nth-child(2)')};
    numeroDocumentoGrid = () => { return cy.get('[data-qa="td-despesa-numero-documento-e-status-0"]')};
    
   
    //----------------------- Retorno de Mensagens apresentadas em tela -------------------------\\
    filtroSemResultado = () => { return cy.get('.texto-404').contains('Não encontramos resultados, verifique os filtros e tente novamente.')};


    //----------------------- Tela Cadastro de Despesa -------------------------\\
    possuiComprovacaoFiscal = () => { return cy.get('[data-qa="cadastro-edicao-despesa-possui-comprovacao-fiscal"]')};
    naoPossuiComprovacaoFiscal = () => { return cy.get('[data-qa="cadastro-edicao-despesa-nao-possui-comprovacao-fiscal"]')};
    despesaReconhecida = () => { return cy.get('[data-qa="cadastro-edicao-despesa-reconhecida-pela-associacao"]')};
    despesaNaoReconhecida = () => { return cy.get('[data-qa="cadastro-edicao-despesa-nao-reconhecida-pela-associacao"]')};
    cadastroFornecedor = () => { return cy.get('[data-qa="cadastro-edicao-despesa-cnpj-cpf-fornecedor"]')};
    cadastroRazaoSocialFornecedor = () => { return cy.get('[data-qa="cadastro-edicao-despesa-razao-social-fornecedor"]')};
    cadastroTipoDocumento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-tipo-de-documento"]')};
    cadastroDataDocumento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-data-do-documento"]')};
    cadastroNumeroDocumento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-numero-do-documento"]')};
    cadastroFormaPagamento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-forma-de-pagamento"]')};
    cadastroDataPagamento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-data-da-transacao"]')};
    cadastroBoletimOcorrencia = () => { return cy.get('[data-qa="cadastro-edicao-despesa-numero-boletim-de-ocorrencia"]')};
    cadastroValorTotalDocumento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-valor-total-do-documento"]')};
    cadastroValorRealizado = () => { return cy.get('[data-qa="cadastro-edicao-despesa-valor-realizado"]')};
    cadastroValorRecursoProprio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-valor-recurso-proprio"]')};
    cadastroNumeroCheque = () => { return cy.get('[data-qa="cadastro-edicao-despesa-numero-do-documento-de-transacao"]')};
    cadastroValorPtrf = () => { return cy.get('[data-qa="cadastro-edicao-despesa-valor-do-ptrf"]')};
    cadastroDadosGasto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-gasto-tem-rateios"]')};
    cadastroTipoAplicacaoRecurso = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-tipo-de-aplicacao-do-recurso"]')};
    cadastroTipoDespesa = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-tipo-de-aplicacao-do-recurso"]')};
    cadastroPossiuVinculo = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-gasto-possui-vinculo-com-atividade-especifica"]')};
    cadastroAtividadeVinculada = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-atividade-vinculada"]')};
    cadastroNaoPossiuVinculo = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-gasto-nao-possui-vinculo-com-atividade-especifica"]')};
    cadastroTipoAplicacaoDespesa2 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-1-tipo-de-aplicacao-do-recurso"]')};
    cadastroTipoAplicacaoDespesa3 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-2-tipo-de-aplicacao-do-recurso"]')};
    cadastroTipoAplicacaoDespesa4 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-3-tipo-de-aplicacao-do-recurso"]')};
    removerDespesa2 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-1-btn-remover-despesa"]')};
    removerDespesa3 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-2-btn-remover-despesa"]')};
    removerDespesa4 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-3-btn-remover-despesa"]')};
    despesaRetemImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-retem-imposto"]')};
    botaoAdicionarImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-btn-adicionar-imposto"]')};
    cadastroEdicaoImpostoDocumento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-tipo-documento"]')};
    cadastroEdicaoEspecificacaoImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-especificacao-do-imposto"]')};
    cadastroEdicaoImpostoFormaPagamento = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-forma-de-pagamento"]')};
    cadastroEdicaoDataPagamentoImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-data-do-pagamento"]')};
    cadastroEdicaoDespesaAcaoImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-acao"]')};
    cadastroEdicaoTipoContaImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-tipo-de-conta"]')};
    cadastroEdicaoValorImposto = () => { return cy.get('[data-qa="cadastro-edicao-despesa-imposto-0-valor-do-imposto"]')};
    cadastrarEstorno = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastrar-estorno"]')};
   
    //----------------------- Cadastro de Despesa Custeio-------------------------\\
    cadastroTipoDespesaCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-tipo-de-despesa"]')};
    cadastroEspecificacaoCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-especificacao-material"]')};
    cadastroAcaoCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-acao"]')};
    cadastroAcaoCusteio2 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-1-cadastro-custeio-acao"]')};
    cadastroTipoContaCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-tipo-conta-utilizada"]')};
    cadastroTipoContaCusteio2 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-1-cadastro-custeio-tipo-conta-utilizada"]')};
    cadastroValorCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-valor"]')};
    cadastroValorCusteio2 = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-1-cadastro-custeio-valor"]')};
    cadastroValorRealizadoCusteio = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-custeio-valor-realizado"]')};
   
    //----------------------- Cadastro de Despesa Capital -------------------------\\
    cadastroEspecificacaoCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-especificacao-material"]')};
    cadastroAcaoCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-acao"]')};
    cadastroQuantidadeItensCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-quantidade-de-itens"]')};
    cadastroValorUnitarioCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-valor-unitario"]')};
    cadastroProcessoCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-numero-do-processo-incorporacao"]')};
    cadastroTipoContaCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-tipo-conta"]')};
    cadastroValorCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-valor"]')};
    cadastroValorRealizadoCapital = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-cadastro-capital-valor-realizado"]')};

    //----------------------- Cadastro de Estorno -------------------------\\
    campoObrigatorioCadastroEstorno = () => { return cy.get('.span_erro').contains('Data do crédito é obrigatório.')};
    dataCadastroEstorno = () => { return cy.get('[data-qa]')};
    calendarioEstorno = () => { return cy.get(':nth-child(5) > .react-datepicker__day--030')};
    deletarEstorno = () => { return cy.get('.btn-danger')};
    excluirCreditoEstorno = () => { return cy.get('.modal-footer > .btn-success')};
    itensEstorno = () => { return cy.get('tbody > tr > :nth-child(1)')};
    acessarEstorno = () => { return cy.get('[data-qa="cadastro-edicao-despesa-rateio-0-acessar-estorno"]')};
    motivosEstorno = () => { return cy.get('.p-multiselect-label')};
    fecharMotivosEstorno = () => { return cy.get('.p-multiselect-close-icon')};
    confirmarMotivosEstorno = () => { return cy.get(':nth-child(2) > .d-flex > .btn-success')};
    cancelarMotivosEstorno = () => { return cy.get(':nth-child(2) > .d-flex > .btn-outline-success')};
    tarifaBancaria = () => { return cy.get(':nth-child(4) > .p-checkbox > .p-checkbox-box')};

    

    
    

}

export default GastosEscolaElementos;