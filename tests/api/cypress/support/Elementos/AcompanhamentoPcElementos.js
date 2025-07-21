class AcompanhamentoPCElementos {

    //----------------------- Botões -------------------------\\
    botaoVerTodasPretacoes = () => { return cy.get('.mt-3 > :nth-child(2) > .btn')}; 
    botaoVerPretacoes1card = () => { return cy.get(':nth-child(1) > .card > .card-body > .text-center > .btn')}; 
    botaoVerPretacoes2card = () => { return cy.get(':nth-child(2) > .card > .card-body > .text-center > .btn')};
    botaoVerPretacoes3card = () => { return cy.get(':nth-child(3) > .card > .card-body > .text-center > .btn')};
    botaoVerPretacoes4card = () => { return cy.get(':nth-child(4) > .card > .card-body > .text-center > .btn')};
    botaoVerPretacoes5card = () => { return cy.get(':nth-child(5) > .card > .card-body > .text-center > .btn')};
    botaoVerPretacoes6card = () => { return cy.get(':nth-child(6) > .card > .card-body > .text-center > .btn')};
    botaoPeriodos = () => { return cy.get('#periodo')};
    botaoRemoverStatus = () => { return cy.get('.ant-select-selection-overflow-item > .ant-select-selection-item > .ant-select-selection-item-remove > .anticon > svg')};  
    botaoRemoverStatus1 = () => { return cy.get(':nth-child(1) > .ant-select-selection-item > .ant-select-selection-item-remove')};
    botaoRemoverStatus2 = () => { return cy.get(':nth-child(2) > .ant-select-selection-item > .ant-select-selection-item-remove')};
    botaoFiltrar = () => { return cy.get('.d-flex').contains('Filtrar')}; 
    botaoAcoes = () => { return cy.get(':nth-child(1) > :nth-child(9) > div > .btn > .svg-inline--fa > path')};
    botaoReabrirPC = () => { return cy.get('#btn-retroceder').contains('Reabrir PC')};
    botaoReabrirConfirmar = () => { return cy.get('.modal-footer > .btn-success').contains('Confirmar')};
    botaoReabrirCancelar = () => { return cy.get('.modal-footer > .btn-outline-success').contains('Cancelar')};
    botaoReceber = () => { return cy.get('.bd-highlight.mb-3 > .p-2 > .btn').contains('Receber')};
    botaoNaoRecebida = () => { return cy.get('#btn-retroceder').contains('Não recebida')};
    botaoRecebida = () => { return cy.get('#btn-retroceder > span').contains('Recebida')};
    botaoConcluirAnalise = () => { return cy.get(':nth-child(3) > .p-2 > .btn').contains('Concluir análise')};
    botaoConclusaoConfirmar = () => { return cy.get(':nth-child(3) > .d-flex > .btn-success').contains('Confirmar')};
    botaoConclusaoCancelar = () => { return cy.get(':nth-child(3) > .d-flex > .btn-outline-success').contains('Cancelar')};
    botaoAdicionarNovoComentario = () => { return cy.get('.d-flex > .btn-success').contains('+ Adicionar novo comentário')};
    botaoNotificarAssociacao = () => { return cy.get('#content > .page-content-inner > form > .d-flex > .btn-outline-success').contains('Notificar a Associação')};
    botaoMaisFiltros = () => { return cy.contains('Mais Filtros')};
    botaoMenosFiltros = () => { return cy.contains('Menos filtros')};
    botaoLimpar = () => {return cy.contains('Limpar')};
    botaoIrParaListagem = () => {return cy.contains('Ir para a listagem')};
    botaoVoltarParaPainelGeral = () => {return cy.get('.p-2.pt-3 > .btn')};
    botaoAnalisar = () => {return cy.get('.bd-highlight.mb-3 > .p-2 > .btn')};
    botaoAdicionarAcerto = () => {return cy.get('.row > .col-12 > .d-flex > .bd-highlight > .btn')};
    botaoDescartarAcerto = () => {return cy.get('.col-12 > .d-flex > .btn-outline-success')};
    botaoSalvar = () => {return cy.get('.col-12 > .row > .col-12 > .d-flex > .btn:nth-child(2)')};
    BotaoLixeira = () => {return cy.get('.dados-extrato-bancario-correcao > .bd-highlight > span > .svg-inline--fa > path')};
    BotaoVoltar = () => {return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-outline-success')};
    BotaoConfirmarExclusao = () => {return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-success')};
    botaoMaisMenosFiltros = () => {return cy.get('.tab-pane > form > .d-flex > .pl-2 > .btn:nth-child(1)')};
    botaoDevolverParaAssociacao = () => {return cy.get('.page-content-inner > .mt-4 > div > .btn > span').contains('Devolver para Associação')};
    botaoVerResumo = () => {return cy.get('.d-flex.mt-4 > :nth-child(2) > .btn')};
    botaoReceberAposAcertos = () => {return cy.get('[data-qa="botao-avancar-acompanhamento-pc"]').contains('Receber após acertos')};
    botaoApresentadaAposAcertos = () => {return cy.get('[data-qa="botao-retroceder-acompanhamento-pc"]').contains('Apresentada após acertos')};



    //----------------------- Campos -------------------------\\
    campoDataRecebimento = () => { return cy.get('[data-qa]')};
    campoFiltro = () => { return cy.get('.ant-select-selection-overflow')};
    selecionarRecebida = () => { return cy.get('div[title="Recebida"]')};
    selecionarEmAnalise = () => { return cy.get('div[title="Em análise"]')};
    selecionarRecebidaAposAcertos = () => { return cy.get('div[title="Recebida após acertos"]')};
    deletarfiltros = () => { return cy.get(':nth-child(1) > .ant-select-selection-item > .ant-select-selection-item-remove > .anticon > svg')};
    campoAcoesRecebida = () => { return cy.get(':nth-child(9) > div > .btn')};
    campoAcoesEmAnalise = () => { return cy.get(':nth-child(1) > :nth-child(9) > div > .btn')};
    campoFiltrarPorUmTermo = () => {return cy.get('.page-content-inner > form > .row > .col:nth-child(1) > .form-control')};
    campoFiltrarPorTipoDeUnidade = () => {return cy.get('#filtrar_por_tipo_de_unidade')}
    campoFiltrarPorStatus = () => {return cy.get('.ant-select-selection-overflow')}
    campoFiltrarPorTecnicoAtribuido = () => {return cy.get('#filtrar_por_tecnico_atribuido')};
    campoFiltrarPorPeriodoInicio = () => {return cy.get('.pr-0 > .react-datepicker-wrapper > .react-datepicker__input-container > [data-qa]')};
    campoFiltrarPorPeriodoFim = () => {return cy.get('.pl-0 > .react-datepicker-wrapper > .react-datepicker__input-container > [data-qa]')};
    campoDataCorrigida = () => {return cy.get('.row > .col-3 > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control')};
    campoSaldoCorrigido = () => {return cy.get('.col-12 > #correcao_extrato_bancario > .row > .col-4 > #saldo_extrato')};
    campoAcao = () => {return cy.get('#filtrar_por_acao')};
    campoFornecedor = () => {return cy.get('#filtrar_por_nome_fornecedor')};
    campoNumeroDeDocumento = () => {return cy.get('#filtrar_por_numero_de_documento')};
    campoPeriodoDePagamentoDataInicio = () => {return cy.get('#data_range')};
    campoPeriodoDePagamentoDataFim = () => {return cy.get(':nth-child(3) > input')};
    campoConferencia = () => {return cy.get(':nth-child(2) > .ant-select > .ant-select-selector > .ant-select-selection-overflow')};
    campoConferenciaListagem = () => {return cy.get('.rc-virtual-list-holder > div > .rc-virtual-list-holder-inner')};
    campoTipoDeLancamento = () => {return cy.get('#filtrar_por_lancamento')};
    campoTipoDeDocumento = () => {return cy.get('#filtrar_por_tipo_de_documento')};
    campoFormaDePagamento = () => {return cy.get('#filtrar_por_tipo_de_pagamento')};
    campoInformacoes = () => {return cy.get(':nth-child(1) > .ant-select > .ant-select-selector > .ant-select-selection-overflow')};
    campoInformacoesListagem = () => {return cy.get('.ant-select-item-option-content')};
    campoInformacoesLimpa = () => {return cy.get(':nth-child(1) > .ant-select > .ant-select-selector')};
    campoPrazoParaReenvio = () => {return cy.get('.d-flex > .flex-grow-1 > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control')};
    campoTecnicoResponsável = () => {return cy.get('[data-qa="tecnico-responsavel"]')};
    campoDataRecebimento = () => {return cy.get('[data-qa="data-de-recebimento"]')};
    campoStatus = () => {return cy.get('[data-qa="select-status"]')};
    campoProcessoSEI = () => {return cy.get('#processo_regularidade')};
    campoUltimaAnalise = () => {return cy.get(':nth-child(10) > .row > :nth-child(2) > .react-datepicker-wrapper > .react-datepicker__input-container > [data-qa]')};
    campoVisualizeDevolucoesDatas = () => {return cy.get('#filtrar_por_tipo_de_ajuste')};
    campoDataRecebimentoDevolutiva = () => {return cy.get('.d-flex > .col > .react-datepicker-wrapper > .react-datepicker__input-container > .form-control')};




    //----------------------- Diversos elementos -------------------------\\
    caixaComentario = () => { return cy.get('#comentario')}; 
    inserirTextoCaixaComentario = () => { return cy.get('[data-qa="input-escrever-novo-comentario"]')};
    inserirTextoCaixaComentario2 = () => { return cy.get('form > div > .form-row > .col > #comentario')};
    cancelarComentario = () => { return cy.get('[data-qa="botao-cancelar-novo-comentario"]').contains('Cancelar')}; 
    botaoConfirmarComentario =  () => { return cy.get('[data-qa="botao-confirmar-novo-comentario"]').contains('Confirmar comentário')};
    editarComentario =  () => { return cy.get(':nth-child(1) > .d-flex > :nth-child(2) > [data-qa="botao-editar-comentario-undefined"]').contains('Editar')};
    modalExcluirComentarioCancelar = () => { return cy.get('[data-qa="modal-excluir-comentario-btn-Cancelar"]')};
    modalExcluirComentarioExcluir =  () => { return cy.get('[data-qa="modal-excluir-comentario-btn-Excluir"]')};
    modalNotificarComentarioSim =  () => { return cy.get('[data-qa="modal-notificar-comentarios-btn-Sim"]')};
    modalNotificarComentarioNao =  () => { return cy.get('[data-qa="modal-notificar-comentarios-btn-Não"]')};
    marcarComentarioNotificar = () => { return  cy.get('.checkbox-comentario-de-analise')};
    caixaSolicitarEnvioDoComprovanteDeSaldoDaConta = () => { return cy.get('.col-12 > .form-check > .form-check-input')};
    caixaObservacao = () => { return cy.get('#observacao_solicitar_envio_do_comprovante_do_saldo_da_conta')};
    tabelaConferenciaFiltros = () => { return cy.get('.tab-pane > .p-datatable > .p-datatable-wrapper > table > .p-datatable-thead')};
    expandirTabelaConferenciaDeLancamentos = () => { return cy.get('.p-datatable-tbody > :nth-child(1) > [style="width: 5%; border-left: none;"]')};
    tabelaConferenciaFiltrosDetalhes = () => {return cy.get('#nav-conferencia-de-lancamentos-tabContent > .tab-pane > .p-datatable > .p-datatable-wrapper > table')};
    checkboxOrdenarComImpostoVinculadosAsDespesas = () => {return cy.get('#checkOerdenarPorImposto')};
    colunaConferenciaDeLancamentos = () => {return cy.get('.p-datatable-row linha-conferencia-de-lancamentos-correto')};
    colunaConferenciaDeLancamentosDataOrdenacao = () => {return cy.get('#nav-conferencia-de-lancamentos-tabContent > .tab-pane > .p-datatable > .p-datatable-wrapper > table > .p-datatable-thead > tr > :nth-child(2)')};
    colunaConferenciaDeLancamentosInformacoesOrdenacao = () => {return cy.get('.p-datatable-thead > tr > :nth-child(6)')};
    colunaConferenciaDeLancamentosValorOrdenacao = () => {return cy.get('.p-datatable-thead > tr > :nth-child(7)')};
    tabelaExtratoBancario = () => {return cy.get('.tr-titulo')};
    dowloadRelatorioAcertos = () => {return cy.get('#nav-historico > .relacao-bens-container > article > .info > .fonte-12 > .btn-editar-membro')};
    verAcertos = () => {return cy.get('#nav-historico > #nav-conferencia-de-lancamentos-tabContent > .tab-pane > #tabela-acertos-lancamentos > .p-datatable-wrapper > table > .p-datatable-tbody > .p-datatable-row:nth-child(1) .p-row-toggler > .p-row-toggler-icon')};
    donwloadRelatorioAcertosAnterior  = () => {return cy.get(':nth-child(18) > article > .info > .fonte-12 > .btn-editar-membro')};
    donwloadRelatorioAposAcertos = () => {return cy.get(':nth-child(19) > article > .info > .fonte-12 > .btn-editar-membro')};
    legendaInformacaoLancamentos = () => {return cy.get('.d-flex > div > span > .d-flex > .legendas-table').contains('Legenda informação')};
    legendaConferenciaLancamentos = () => {return cy.get('.tab-pane > .d-flex > div > span > .legendas-table').contains('Legenda conferência')};
    legendaConferenciaDocumentos = () => {return cy.get('.page-content-inner > .d-flex > div > span > .legendas-table').contains('Legenda conferência')};
    botaoFecharLegenda = () => {return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn')};
    pagina2LancamentosResumo = () => {return cy.get('#nav-historico > #nav-conferencia-de-lancamentos-tabContent > .tab-pane > #tabela-acertos-lancamentos > .p-paginator > .p-paginator-pages > :nth-child(2)')};
    pagina2DocumentosResumo = () => {return cy.get('#nav-historico > #tabela-acertos-documentos > .p-paginator > .p-paginator-pages > .p-highlight')};


    
    
    //----------------------- Modal -------------------------\\
    modalEdicaoComentarioInserir = () => { return     cy.get('.modal-content > .modal-body > .row > .col-12 > .form-control')};
    modalEdicaoComentarioBotaoApagar = () => { return cy.get('.modal-body > .d-flex > :nth-child(1) > .btn').contains('Apagar')};
    modalEdicaoComentarioBotaoCancelar = () => { return cy.get('.modal-body > .d-flex > :nth-child(2) > .btn').contains('Cancelar')};
    modalEdicaoComentarioBotaoSalvar = () => { return cy.get('.modal-body > .d-flex > :nth-child(3) > .btn').contains('Salvar')};

    modalExcluirComentarioBotaoCancelar = () => { return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-outline-success').contains('Cancelar')};
    modalExcluirComentarioBotaoExluir = () => { return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-danger').contains('Excluir')};

    marcarComentario = () => { return cy.get(':nth-child(1) > .d-flex > [data-qa="comentario-undefined"] > [data-qa="checkbox-comentario-undefined"]')};
    modalNotificarComentariosBotaoSim = () => { return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-outline-success').contains('Sim')};
    modalNotificarComentariosBotaoNao = () => { return cy.get('.fade > .modal-dialog > .modal-content > .modal-footer > .btn-success').contains('Não')};

    modalConclusao = () => { return cy.get(':nth-child(1) > #status')};
    motivoConclusao = () => { return cy.get('.p-multiselect-label')};
    motivoCampoConclusao = () => { return cy.get('.p-multiselect-items > :nth-child(1) > .p-checkbox > .p-checkbox-box')};
    motivoCampoConclusaoReprovar = () => { return cy.get('.p-multiselect-items > :nth-child(1) > .p-checkbox > .p-checkbox-box')};
    motivoCampoRecomendacoes = () => { return cy.get('.col-12.mt-2 > .form-control')};
    confirmarConclusao = () => { return cy.get(':nth-child(2) > .d-flex > .btn-success')};
    cancelarConclusao = () => { return cy.get(':nth-child(2) > .d-flex > .btn-outline-success')};


    //----------------------- Card/colapse -------------------------\\
    cardPrestacoesDeContasRecebidasAguardandoAnalise = () => { return cy.get('.card-header').contains('Prestações de contas recebidas aguardando análise')}; 
    cardPrestacoesDeContasEmAnalise = () => { return cy.get('.card-header').contains('Prestações de contas em análise')}; 

    colapseSinteseDoPeriodoDeRealizacaoDaDespesa = () => { return cy.get('#accordion_sintese_por_realizacao_da_despesa > .card > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    colapseSinteseDoPeriodoPorAcao = () => { return cy.get('#accordion_sintese_por_acao > :nth-child(1) > :nth-child(1) > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    
    subcolapse1 = () => { return cy.get('#accordionResumoFinanceiroTabelaAcoes > :nth-child(1) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    subcolapse2 = () => { return cy.get(':nth-child(2) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    subcolapse3 = () => { return cy.get(':nth-child(3) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')};
    subcolapse4 = () => { return cy.get(':nth-child(4) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    subcolapse5 = () => { return cy.get(':nth-child(5) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')}; 
    subcolapse6 = () => { return cy.get(':nth-child(6) > #headingOne > .mb-0 > .row > .col-1 > .btn > .span-icone-toogle')};  
    olhoExtratoBancarioDaContaCheque = () => { return cy.get(':nth-child(3) > .col-12 > .d-flex > :nth-child(2)')};
    Xmodal = () => { return cy.get('.close > [aria-hidden="true"]')}; 
    dowloadExtratoBancarioDaContaCheque = () => { return cy.get(':nth-child(3) > .col-12 > .d-flex > :nth-child(4)')}; 
    
    lupa1 = () => { return cy.get(':nth-child(1) > [style="width: 150px;"] > .d-flex > :nth-child(1)')};
    lupa2 = () => { return cy.get(':nth-child(2) > [style="width: 150px;"] > .d-flex > :nth-child(1)')};
    lupa3 = () => { return cy.get(':nth-child(3) > [style="width: 150px;"] > .d-flex > :nth-child(1)')};
    lupa4 = () => { return cy.get(':nth-child(4) > [style="width: 150px;"] > .d-flex > :nth-child(1)')};

    baixarArquivo1 = () => { return cy.get(':nth-child(1) > [style="width: 150px;"] > .d-flex > :nth-child(3) > .svg-inline--fa > path')};
    baixarArquivo2 = () => { return cy.get(':nth-child(2) > [style="width: 150px;"] > .d-flex > :nth-child(3) > .svg-inline--fa > path')};
    baixarArquivo3 = () => { return cy.get(':nth-child(3) > [style="width: 150px;"] > .d-flex > :nth-child(3) > .svg-inline--fa > path')};
    baixarArquivo4 = () => { return cy.get(':nth-child(4) > [style="width: 150px;"] > .d-flex > :nth-child(3) > .svg-inline--fa > path')};

    abaConferenciaDeLancamentosContaCheque = () => { return cy.get('#nav-tab-conferencia-de-lancamentos').contains('Conta Cheque')};
    abaConferenciaDeLancamentosContaCartao = () => { return cy.get('#nav-tab-conferencia-de-lancamentos').contains('Conta Cartão')}; 
    
     

    //-------------------------- Validações ------------------------\\
    validaFiltrarSemInfo = () => {return cy.contains('Nenhuma prestação retornada. Tente novamente com outros filtros')};
    validaFiltrarPorTipoDeUnidade = () => {return cy.contains('EMEF ALTINO ARANTES')};
    validaFiltrarPorumTermoComInfo = () => {return cy.contains('JARDIM CLIMAX II')};
    validaFiltrarPorStatus = () => {return cy.contains('JARDIM CLIMAX II')};
    validaFiltrarPorTecnicoAtribuido = () => {return cy.contains('CEI DIRET 13 DE MAIO')};
    validaFiltroPorPeriodo = () => {return cy.contains('EMEF ALTINO ARANTES')};
    validaMenosFiltros1 = () => {return cy.contains('Filtrar por técnico atribuído')};
    validaMenosFiltros2 = () => {return cy.contains('Filtrar por período') };
    validaCampoTabelaDataOrdenacao = () => {return cy.get(':nth-child(1) > :nth-child(2) > .p-1')};
    validaCampoTabelaInformacoesOrdenacao = () => {return cy.get('.p-datatable-tbody > :nth-child(1) > [style="width: 15%;"]')};
    validaCampoTabelaValorOrdenacao = () => {return cy.get('.p-datatable-tbody > :nth-child(1) > :nth-child(7)')};
    validaModalMudancaDeStatus = () => {return cy.contains('Mudança de Status').and.contains('Ao notificar a Associação sobre as ”Devolução para Acertos" dessa prestação de contas, será reaberto o período para que a Associação possa realizar os ajustes pontuados até o prazo determinado.').and.contains('A prestação será movida para o status de ”Devolução para Acertos” e ficará nesse status até a Associação realizar um novo envio. Deseja continuar?')};
    validaModalMudancaDeStatusCancela = () => {return cy.contains('Cancelar')};
    validaModalMudancaDeStatusConfirma = () => {return cy.contains('Confirmar')};
    validaTooltipStatusDevolvidaParaAcerto = () => {return cy.contains('Status alterado com sucesso').and.contains('A prestação de conta foi alterada para “Devolvida para acertos”.')};
    validaCardPCDevolvidasParaAcertos = () => {return cy.contains('Prestações de conta devolvidas para acertos')};
    validaStatusPCDevolvidaParaAcertos = () => {return cy.get('.span-status-DEVOLVIDA > strong')};
    validaStatusPCApresentadaAposAcertos = () => {return cy.get('.span-status-DEVOLVIDA_RETORNADA > strong')};
    validaStatusPCRecebidaAposAcertos = () => {return cy.get('.span-status-DEVOLVIDA_RECEBIDA > strong')};

    validaCamposDetalhesTabelaConferenciaLancamentos() {
        cy.contains('CNPJ / CPF').should('be.visible');
        cy.contains('Tipo de documento').should('be.visible');
        cy.contains('Forma de pagamento').should('be.visible');
        cy.contains('Data do pagamento').should('be.visible');
        cy.contains('Número do documento:').should('be.visible');
        cy.contains('Tipo de despesa:').should('be.visible');
        cy.contains('Especificação:').should('be.visible');
        cy.contains('Tipo de aplicação').should('be.visible');
        cy.contains('Demonstrado').should('be.visible');
        cy.contains('Tipo de ação:').should('be.visible');
        cy.contains('Vínculo a atividade').should('be.visible');
    };

    validalegendaInformacaoLancamentos() {
        cy.contains('Legenda informação');
        cy.contains('Antecipado');
        cy.contains('Data do pagamento anterior à data do documento.');
        cy.contains('Estornado');
        cy.contains('Despesa estornada.');
        cy.contains('Parcial');
        cy.contains('Parte da despesa paga com recursos próprios ou de mais de uma conta.');
        cy.contains('Serviço com imposto');
        cy.contains('Despesa com recolhimento de imposto.');
        cy.contains('Imposto Pago');
        cy.contains('Imposto recolhido relativo a uma despesa de serviço.');
        cy.contains('Imposto a ser pago');
        cy.contains('Imposto sem data de pagamento.');
        cy.contains('Excluído');
        cy.contains('Lançamento excluído.');
        cy.contains('Não Reconhecida');
        cy.contains('Despesa não reconhecida pela associação.');
        cy.contains('Sem comprovação fiscal');
        cy.contains('Despesa sem comprovação fiscal.');
        cy.contains('Conciliada');
        cy.contains('Despesa com conciliação bancária realizada.');
        cy.contains('Não conciliada');
        cy.contains('Despesa sem conciliação bancária realizada.');
    };

    validalegendaConferenciaLancamentos() {
        cy.contains('Legenda da Conferência de Lançamentos');
        cy.contains('O lançamento possui acertos para serem conferidos.');
        cy.contains('O lançamento está correto e/ou os acertos foram conferidos.');
        cy.contains('O lançamento possui acerto(s) que foram conferidos automaticamente pelo sistema.');
        cy.contains('Não conferido.');
    };

    validalegendaConferenciaDocumentos() {
        cy.contains('Legenda da Conferência de Documentos');
        cy.contains('O documento possui acertos para serem conferidos.');
        cy.contains('O documento está correto e/ou os acertos foram conferidos.');
        cy.contains('Não conferido.');
    };

    validaSintesePeriodoRealizacaoDespesa() {
        cy.contains('Extrato Bancário da Unidade');
        cy.contains('Data');
        cy.contains('Saldo');
        cy.contains('Diferença em relação à prestação de contas');
        cy.contains('Custeio (R$)');
        cy.contains('Capital (R$)');
        cy.contains('Livre aplicação (R$)');
        cy.contains('Total (R$)');
        cy.contains('Saldo inicial (reprogramado do período anterior)');
        cy.contains('Repasses');
        cy.contains('Demais créditos');
        cy.contains('Despesas');
        cy.contains('Saldo final');
        cy.contains('Despesas não demonstradas');
        cy.contains('Saldo reprogramado (para o próximo período)');
    };

    validaSintesePeriodoRealizacaoDespesaRecebidaAposAcertos() {
        cy.contains('Extrato Bancário da Unidade');
        cy.contains('Data');
        cy.contains('Saldo');
        cy.contains('Diferença em relação à prestação de contas');
    };

    validaSintesePeriodoPorAcao() {
        cy.contains('PTRF Básico').should('be.visible');
        cy.contains('Rolê Cultural').should('be.visible');
        cy.contains('Formação').should('be.visible');
        cy.contains('Material Pedagógico').should('be.visible');
        cy.contains('Salas e Espaços de Leitura').should('be.visible');
        cy.contains('Material Complementar').should('be.visible');
    };

    validaNomeDoArquivo() {
        cy.contains('Nome do arquivo').should('be.visible');
        cy.contains('Demonstrativo Financeiro da Conta Cheque').should('be.visible');
        cy.contains('Relação de Bens da Conta Cheque').should('be.visible');
        cy.contains('Ata de apresentação da prestação de conta').should('be.visible');
        cy.contains('Ata de retificação da prestação de conta').should('be.visible');
    };
    
    validaConferenciaDocumentos() {
        cy.contains('Nome do Documento').should('be.visible');
        cy.contains('Conferido').should('be.visible');
        cy.contains('Adicionar ajuste').should('be.visible');
        cy.contains('Demonstrativo Financeiro da Conta Cheque').should('be.visible');
        cy.contains('Demonstrativo Financeiro da Conta Cartão').should('be.visible');
        cy.contains('Ata da Prestação de Contas e Parecer do Conselho Fiscal da Associação').should('be.visible');
        cy.contains('Extrato ou demonstrativo da Conta Cheque').should('be.visible');
        cy.contains('Extrato ou demonstrativo da Conta Cartão').should('be.visible');
        cy.contains('Ata do Plano Anual de Atividades - PAA').should('be.visible');
        cy.contains('Relação de Bens adquiridos ou produzidos da Conta Cheque').should('be.visible');
    };

    validaVerResumoDeAcertos() {
        cy.contains('Resumo de acertos');
        cy.contains('Histórico');
        cy.contains('Visualize as devoluções pelas datas:');
        cy.contains('Versão da devolução:');
        cy.contains('Data de devolução da DRE:');
        cy.contains('Prazo para reenvio:');
        cy.contains('Data de devolução da UE:');
        cy.contains('Acertos nos lançamentos');
    };




}

export default AcompanhamentoPCElementos;