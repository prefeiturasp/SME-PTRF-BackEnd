//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Parametros = new ComumElementosPTRF

import AcompanhamentoPcElementos from "../Elementos/AcompanhamentoPcElementos";
const AcompanhamentoPC = new AcompanhamentoPcElementos


class AcompanhamentoPcPagina {

    validarPrestacoesContasNaoRecebidasPcAbertas() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.botaoAcoes().click();
        AcompanhamentoPC.botaoReabrirPC().click();
        AcompanhamentoPC.botaoReabrirCancelar().click();
        AcompanhamentoPC.botaoReabrirPC().click();
        AcompanhamentoPC.botaoReabrirConfirmar().click();
    }

    validarPrestacoesContasNaoRecebidasStatusReceberPc() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.botaoAcoes().click();
        AcompanhamentoPC.campoDataRecebimento().type('20/10/2023');
        AcompanhamentoPC.botaoReceber().click();
    }

    validarPrestacoesContasRecebidasStatusNaoRecebida() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarRecebida().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.campoAcoesRecebida().click();
        AcompanhamentoPC.botaoNaoRecebida().click();
        AcompanhamentoPC.botaoReabrirCancelar().click();
        AcompanhamentoPC.botaoNaoRecebida().click();
        AcompanhamentoPC.botaoReabrirConfirmar().click();
    }

    validarPrestacoesContasRecebidasStatusPcAnalisar() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarRecebida().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
    }

    validarPrestacoesContasEmAnaliseStatusRecebida() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        cy.wait(1000)
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        cy.wait(4000)
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarEmAnalise().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.campoAcoesEmAnalise().click();
        AcompanhamentoPC.botaoRecebida().click();
        AcompanhamentoPC.botaoReabrirCancelar().click();
        AcompanhamentoPC.botaoReabrirConfirmar().click();
    }

    validarPrestacoesContasEmAnaliseStatusAprovar() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarEmAnalise().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.campoAcoesEmAnalise().click();
        AcompanhamentoPC.botaoConcluirAnalise().click();
        AcompanhamentoPC.modalConclusao().select('Aprovada');
        AcompanhamentoPC.confirmarConclusao().click();
    }

    validarPrestacoesContasEmAnaliseStatusAprovarComRessalvas() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarEmAnalise().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.campoAcoesEmAnalise().click();
        AcompanhamentoPC.botaoConcluirAnalise().click();
        AcompanhamentoPC.modalConclusao().select('Aprovada com ressalvas');
        AcompanhamentoPC.motivoConclusao().click();
        AcompanhamentoPC.motivoCampoConclusao().click();
        AcompanhamentoPC.motivoConclusao().click();
        AcompanhamentoPC.motivoCampoRecomendacoes().type('Testes');
        AcompanhamentoPC.botaoConclusaoConfirmar().click();
    }

    validarPrestacoesContasEmAnaliseStatusReprovar() {
        AcompanhamentoPC.botaoVerTodasPretacoes().click();
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoRemoverStatus2().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.selecionarEmAnalise().click();
        AcompanhamentoPC.campoFiltro().click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.campoAcoesEmAnalise().click();
        AcompanhamentoPC.botaoConcluirAnalise().click();
        AcompanhamentoPC.modalConclusao().select('Reprovada');
        AcompanhamentoPC.motivoConclusao().click();
        AcompanhamentoPC.motivoCampoConclusaoReprovar().click();
        AcompanhamentoPC.motivoConclusao().click();
        AcompanhamentoPC.botaoConclusaoConfirmar().click();
    }

    validarPCRecebidasStatusAguardandoAnalise() {
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoVerPretacoes2card().click();
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000)
        AcompanhamentoPC.botaoAdicionarNovoComentario().click();
        AcompanhamentoPC.caixaComentario().type('teste automatizado');
        AcompanhamentoPC.cancelarComentario().click();
        cy.wait(1000)
        AcompanhamentoPC.botaoAdicionarNovoComentario().click();
        AcompanhamentoPC.caixaComentario().type('teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click(); //confirmar comentario
        AcompanhamentoPC.editarComentario().click() // editar
        AcompanhamentoPC.modalEdicaoComentarioBotaoCancelar().click(); // modal botao cancelar 
        AcompanhamentoPC.editarComentario().click() // editar
        AcompanhamentoPC.modalEdicaoComentarioInserir().clear().type('teste automatizado-editado');
        AcompanhamentoPC.modalEdicaoComentarioBotaoSalvar().click(); // modal botao salvar
        AcompanhamentoPC.editarComentario().click() // editar
        AcompanhamentoPC.modalEdicaoComentarioBotaoApagar().click() //apagar
        AcompanhamentoPC.modalExcluirComentarioBotaoCancelar().click() // cancela a exclusao
        AcompanhamentoPC.modalEdicaoComentarioBotaoApagar().click() //apagar
        AcompanhamentoPC.modalExcluirComentarioBotaoExluir().click() // excluir
        cy.wait(300)
        AcompanhamentoPC.botaoAdicionarNovoComentario().click();
        AcompanhamentoPC.caixaComentario().type('teste automatizado novo comentário 01');
        AcompanhamentoPC.botaoConfirmarComentario().click(); //confirmar comentario
        AcompanhamentoPC.marcarComentario().check() // marcar comentario
        cy.wait(1000)
        AcompanhamentoPC.botaoNotificarAssociacao().click() // botao notificar
        AcompanhamentoPC.modalNotificarComentariosBotaoNao().click() // modal notificar comentarios > botao nao
        AcompanhamentoPC.botaoNotificarAssociacao().click() // botao notificar
        AcompanhamentoPC.modalNotificarComentariosBotaoSim().click() // modal notificar comentarios > botao sim
        cy.contains('Comentários já notificados').should('be.visible') // apresenta comentário notificado
        cy.contains('Notificado').should('be.visible') // apresenta comentário notificado
        cy.contains('teste automatizado novo comentário 01').should('be.visible') // apresenta comentário notificado

    }

    validarPCRecebidasFiltrosBotoesAcao() {
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoVerPretacoes2card().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoMaisFiltros().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('teste'); // campo Filtrar por um termo
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltrarSemInfo().should('be.visible'); //validação - sem info
        AcompanhamentoPC.campoFiltrarPorUmTermo().clear().type('JARDIM CLIMAX II'); // campo Filtrar por um termo
        AcompanhamentoPC.botaoFiltrar().click();   
        //AcompanhamentoPC.validaFiltrarPorumTermoComInfo().should('be.visible'); //validação - com info
        AcompanhamentoPC.botaoLimpar().click();// teste 02- filtrar por tipo de unidade
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('EMEBS');
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltrarSemInfo().should('be.visible'); //validação - sem info 
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('EMEF');
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltrarPorTipoDeUnidade().should('be.visible'); // validação - com info
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.botaoRemoverStatus().click(); // teste 03- filtrar por status
        AcompanhamentoPC.campoFiltrarPorStatus().click({force: true})
        cy.contains('Recebida após acertos').click();
        cy.get('.page-content-inner').click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltrarSemInfo().should('be.visible'); //validação - sem info
        AcompanhamentoPC.botaoRemoverStatus().click();
        AcompanhamentoPC.campoFiltrarPorStatus().click()
        cy.contains('Recebida').click();
        cy.get('.page-content-inner').click();
        AcompanhamentoPC.botaoFiltrar().click();
        //AcompanhamentoPC.validaFiltrarPorStatus().should('be.visible');//validação - com info
        cy.wait(300);
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.campoFiltrarPorTecnicoAtribuido().select('DANIELA CRISTIANE ZOLI FERREIRA') // teste 04- filtrar por tecnico atribuido
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(300);
        AcompanhamentoPC.validaFiltrarSemInfo().should('be.visible'); //validação - sem info
        AcompanhamentoPC.botaoRemoverStatus().click();
        AcompanhamentoPC.campoFiltrarPorTecnicoAtribuido().select('DANIELA CRISTIANE ZOLI FERREIRA')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(300);
        AcompanhamentoPC.validaFiltrarPorTecnicoAtribuido().should('be.visible'); //validação - com info
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(300);
        AcompanhamentoPC.campoFiltrarPorStatus().click() // teste 05- filtrar por periodo
        cy.contains('Recebida').click();
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().type('01/03/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().type('01/05/2023');
        cy.get('.page-content-inner').click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltrarSemInfo().should('be.visible'); //validação - sem info
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().type('20/10/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().type('20/12/2023');
        cy.get('.page-content-inner').click();
        AcompanhamentoPC.botaoFiltrar().click();
        AcompanhamentoPC.validaFiltroPorPeriodo().should('be.visible'); //validação - com info
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.botaoMenosFiltros().click(); // teste 06- botao menos filtros
        AcompanhamentoPC.validaMenosFiltros1().should('not.be.visible')
        AcompanhamentoPC.validaMenosFiltros2().should('not.be.visible')
        AcompanhamentoPC.botaoMaisFiltros().click(); // teste 07- botao de mais filtros
        AcompanhamentoPC.validaMenosFiltros1().should('be.visible')
        AcompanhamentoPC.validaMenosFiltros2().should('be.visible')
        cy.wait(300);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('teste'); // teste 08- botao limpar 
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('EMEBS')
        AcompanhamentoPC.campoFiltrarPorTecnicoAtribuido().select('DANIELA CRISTIANE ZOLI FERREIRA')
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().type('20/10/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().type('20/12/2023');
        cy.get('.page-content-inner').click();
        AcompanhamentoPC.botaoLimpar().click();
        AcompanhamentoPC.campoFiltrarPorUmTermo().should('be.empty')
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().contains('Selecione um tipo')
        AcompanhamentoPC.campoFiltrarPorTecnicoAtribuido().contains('Selecione um servidor')
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().should('be.empty')
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().should('be.empty')

    }

    validarPCRecebidasQuantitativoCardsInalterado() {
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.cardPrestacoesDeContasRecebidasAguardandoAnalise().should('be.visible').parent()
        AcompanhamentoPC.botaoVerPretacoes2card().click();
        cy.wait(300);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(300)
        AcompanhamentoPC.botaoNaoRecebida().click();
        cy.contains('Não receber Prestação de Contas').should('be.visible')
        cy.contains('Atenção, a prestação de contas voltará para o status de Não recebida. As informações de recebimento serão perdidas. Confirma operação?').should('be.visible')
        cy.contains('Cancelar').click()
        cy.contains('Recebida e aguardando análise').should('be.visible')
        AcompanhamentoPC.botaoIrParaListagem().click()
        cy.wait(300)
        AcompanhamentoPC.botaoVoltarParaPainelGeral().click()
        cy.wait(1000)
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.cardPrestacoesDeContasRecebidasAguardandoAnalise().should('be.visible').parent()

    }
    
    validarPCRecebidasQuantitativoCardsAlterado() {
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.cardPrestacoesDeContasRecebidasAguardandoAnalise().should('be.visible').parent()
        AcompanhamentoPC.cardPrestacoesDeContasEmAnalise().should('be.visible').parent()
        AcompanhamentoPC.botaoVerPretacoes2card().click();
        cy.wait(300);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('EMEI BRENNO FERRAZ DO AMARAL'); // campo Filtrar por um termo
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(300)
        AcompanhamentoPC.botaoAcoes().click();
        AcompanhamentoPC.botaoAnalisar().click()
        cy.contains('Status alterado com sucesso').should('be.visible')
        cy.contains('A prestação de conta foi alterada para “Em análise”.').should('be.visible')
        cy.contains('Em análise').should('be.visible')
        cy.wait(6000)
        AcompanhamentoPC.botaoIrParaListagem().click()
        cy.wait(300)
        AcompanhamentoPC.botaoVoltarParaPainelGeral().click()
        cy.wait(1000)
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.cardPrestacoesDeContasRecebidasAguardandoAnalise().should('be.visible').parent().contains('3');
        AcompanhamentoPC.cardPrestacoesDeContasEmAnalise().should('be.visible').parent().contains('49');
        AcompanhamentoPC.botaoVerPretacoes3card().click(); // voltar PC para situação anterior ao teste - roolback teste e2e
        cy.wait(300)
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('EMEI BRENNO FERRAZ DO AMARAL'); // campo Filtrar por um termo
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(300)
        AcompanhamentoPC.botaoAcoes().click();
        AcompanhamentoPC.botaoRecebida().click();
        cy.contains('Confirmar').click();
        cy.contains('Status alterado com sucesso').should('be.visible')
        cy.contains('A prestação de conta foi alterada para “Recebida”.').should('be.visible')
        AcompanhamentoPC.botaoIrParaListagem().click()
        cy.wait(300)
        AcompanhamentoPC.botaoVoltarParaPainelGeral().click()
        cy.wait(1000)
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.cardPrestacoesDeContasRecebidasAguardandoAnalise().should('be.visible').parent().contains('4')  
        AcompanhamentoPC.cardPrestacoesDeContasEmAnalise().should('be.visible').parent().contains('48')  

    }

        validarPCEmAnaliseParte1MateriaisDeReferencia() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000)
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        AcompanhamentoPC.olhoExtratoBancarioDaContaCheque().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.dowloadExtratoBancarioDaContaCheque().click();
        AcompanhamentoPC.botaoAdicionarAcerto().click();
        AcompanhamentoPC.botaoDescartarAcerto().click();
        AcompanhamentoPC.botaoAdicionarAcerto().click();
        AcompanhamentoPC.campoDataCorrigida().click();
        AcompanhamentoPC.campoDataCorrigida().type('20/03/2024');
        AcompanhamentoPC.campoSaldoCorrigido().click();
        AcompanhamentoPC.campoSaldoCorrigido().type('R$78.888,00');
        AcompanhamentoPC.botaoSalvar().click();
        AcompanhamentoPC.BotaoLixeira().click();
        AcompanhamentoPC.BotaoVoltar().click();
        AcompanhamentoPC.BotaoLixeira().click();
        AcompanhamentoPC.BotaoConfirmarExclusao().click();
        AcompanhamentoPC.botaoAdicionarAcerto().click();
        AcompanhamentoPC.caixaSolicitarEnvioDoComprovanteDeSaldoDaConta().check();
        AcompanhamentoPC.caixaObservacao().type('observação teste automatizado');
        AcompanhamentoPC.botaoSalvar().click();
        cy.contains('Salvo com sucesso').should('be.visible');
        AcompanhamentoPC.BotaoLixeira().click();
        AcompanhamentoPC.BotaoConfirmarExclusao().click();
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        cy.wait(300)
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        cy.contains('PTRF Básico').should('be.visible');
        cy.contains('Rolê Cultural').should('be.visible');
        cy.contains('Formação').should('be.visible');
        cy.contains('Material Pedagógico').should('be.visible');
        cy.contains('Salas e Espaços de Leitura').should('be.visible');
        cy.contains('Material Complementar').should('be.visible');
        AcompanhamentoPC.subcolapse1().dblclick();
        AcompanhamentoPC.subcolapse2().dblclick();
        AcompanhamentoPC.subcolapse3().dblclick();
        AcompanhamentoPC.subcolapse4().dblclick();
        AcompanhamentoPC.subcolapse5().dblclick();
        AcompanhamentoPC.subcolapse6().dblclick();
        cy.contains('Nome do arquivo').should('be.visible');
        cy.contains('Demonstrativo Financeiro da Conta Cheque').should('be.visible');
        cy.contains('Ata de retificação da prestação de conta').should('be.visible');
        AcompanhamentoPC.lupa1().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa2().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.baixarArquivo1().click();
        AcompanhamentoPC.baixarArquivo2().click();

    }

    validarPCEmAnaliseConferenciaLancamentoContaCartaoFiltros1() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click(); //step1
        AcompanhamentoPC.botaoAcoes().click(); //step2
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCartao().click();
        cy.wait(300);
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        cy.contains('Filtrar').click(); //step3
        cy.wait(300);
        cy.contains('Exibindo 1 lançamentos').should('be.visible');
        cy.contains('Legenda informação').should('be.visible');
        cy.contains('Legenda conferência').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Data').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Tipo de lançamento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('N.º do documento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Descrição').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Informações').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Valor (R$)').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Conferido').should('be.visible');
        AcompanhamentoPC.botaoMaisMenosFiltros().click(); //step4
        cy.contains('Tipo de lançamento').should('be.visible');
        cy.contains('Ação').should('be.visible');
        cy.contains('Fornecedor')
        cy.contains('Número de documento').should('be.visible');
        cy.contains('Tipo de documento').should('be.visible');
        cy.contains('Forma de pagamento').should('be.visible');
        cy.contains('Período de pagamento').should('be.visible');
        cy.contains('Informações').should('be.visible');
        cy.contains('Conferência').should('be.visible');
        AcompanhamentoPC.campoTipoDeLancamento().select('Créditos'); // step5
        cy.contains('Filtrar').click();
        cy.wait(300);
        cy.contains('Exibindo 1 lançamentos').should('be.visible');
        cy.contains('Legenda informação').should('be.visible');
        cy.contains('Legenda conferência').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Data').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Tipo de lançamento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('N.º do documento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Descrição').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Informações').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Valor (R$)').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().contains('Conferido').should('be.visible');
        AcompanhamentoPC.botaoMaisMenosFiltros().click(); //step6 - selecionar alguns filtros
        AcompanhamentoPC.campoTipoDeLancamento().select('Créditos');
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        AcompanhamentoPC.campoTipoDeDocumento().select('NF');
        AcompanhamentoPC.campoFormaDePagamento().select('DOC/TED/PIX');
        AcompanhamentoPC.campoInformacoes().click()
        AcompanhamentoPC.campoInformacoesListagem().contains('Imposto Pago').click();
        cy.contains('Filtrar').click();
        cy.wait(300);
        cy.contains('Exibindo 0 lançamentos').should('be.visible');
        
    }

    validarPCEmAnaliseConferenciaLancamentoContaCartaoFiltros2() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCartao().click();
        cy.wait(300);
        AcompanhamentoPC.botaoMaisMenosFiltros().click(); //step7 - selecionar todos os filtros
        AcompanhamentoPC.campoTipoDeLancamento().select('Créditos');
        AcompanhamentoPC.campoAcao().select('Recurso Externo');
        AcompanhamentoPC.campoFornecedor().type('Banco do Brasil');
        AcompanhamentoPC.campoNumeroDeDocumento().type('123456');
        AcompanhamentoPC.campoTipoDeDocumento().select('Comprovante');
        AcompanhamentoPC.campoFormaDePagamento().select('Transferência entre contas BB');
        cy.contains('Período de pagamento').click();
        AcompanhamentoPC.campoInformacoes().click()
        AcompanhamentoPC.campoInformacoesListagem().contains('Excluído').click();
        cy.contains('Período de pagamento').click();
        AcompanhamentoPC.campoConferencia().click();
        AcompanhamentoPC.campoConferenciaListagem().contains('Não conferido').click();
        cy.contains('Período de pagamento').click();
        cy.contains('Filtrar').click();
        cy.wait(1000);
        cy.contains('Exibindo 0 lançamentos').should('be.visible');
   
    }

    validarPCEmAnaliseConferenciaLancamentoContaChequeFiltros3() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCheque().click();
        cy.wait(300);
        AcompanhamentoPC.campoAcao().select('PTRF Básico'); // step8
        cy.contains('Filtrar').click();
        cy.wait(300);
        cy.contains('Exibindo 43 lançamentos').should('be.visible');              
        cy.contains('Legenda informação').should('be.visible');
        cy.contains('Legenda conferência').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Data').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Tipo de lançamento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('N.º do documento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Descrição').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Informações').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Valor (R$)').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Conferido').should('be.visible');
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(1000);
        cy.contains('Detalhamento do crédito').should('be.visible');
        cy.contains('Classificação do crédito').should('be.visible'); 
        cy.contains('Tipo de ação').should('be.visible');
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.contains('Crédito').should('be.visible');
        cy.contains('Gasto').should('be.visible');
        cy.wait(300);
   
    }

    validarPCEmAnaliseConferenciaLancamentoContaChequeFiltros4() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCheque().click();
        cy.wait(1000);
        cy.contains('Exibindo 44 lançamentos').should('be.visible');    
        AcompanhamentoPC.botaoMaisMenosFiltros().click(); //step10-step11-step12
        AcompanhamentoPC.campoTipoDeLancamento().select('Gastos');
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        AcompanhamentoPC.campoFornecedor().type('Banco do Brasil');
        AcompanhamentoPC.campoTipoDeDocumento().select('Extrato');
        AcompanhamentoPC.campoFormaDePagamento().select('Débito em conta');
        cy.contains('Período de pagamento').click();
        AcompanhamentoPC.campoInformacoes().click()
        AcompanhamentoPC.campoInformacoesListagem().contains('Conciliada').click();  
        AcompanhamentoPC.campoConferencia().click();
        AcompanhamentoPC.campoConferenciaListagem().contains('O lançamento está correto e/ou os acertos foram conferidos.').click();
        cy.contains('Informações').click();
        cy.contains('Filtrar').click();
        cy.wait(300);
        cy.contains('Exibindo 8 lançamentos').should('be.visible');      
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Data').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Tipo de lançamento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('N.º do documento').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Descrição').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Informações').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Valor (R$)').should('be.visible');
        AcompanhamentoPC.tabelaConferenciaFiltros().parent().contains('Conferido').should('be.visible');
        cy.wait(1000);
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(1000);
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
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(300);
        cy.contains('Gasto').should('be.visible');
        cy.contains('BANCO DO BRASIL S/A').should('be.visible');
        cy.contains('Conciliada').should('be.visible');
        cy.contains('69,75').should('be.visible');
        cy.wait(300);
   
    }

    validarPCEmAnaliseConferenciaLancamentoContaChequeOrdenacao() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCheque().click();
        cy.wait(1000);
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().click();
        cy.wait(1000);
        cy.contains('Exibindo 44 lançamentos').should('be.visible');    
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('02/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('29/12/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().should('be.empty');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().contains('-');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('9,88');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('12.545,40');
   
    }

    validarPCEmAnaliseConferenciaLancamentoContaCartaoOrdenacao() {
        AcompanhamentoPC.botaoPeriodos().select('2023.1 - 01/01/2023 até 30/04/2023');
        AcompanhamentoPC.botaoVerPretacoes3card().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        AcompanhamentoPC.abaConferenciaDeLancamentosContaCartao().click();
        cy.wait(1000);
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().click();
        cy.wait(1000);
        // cy.contains('Exibindo 16 lançamentos').should('be.visible');    
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        // AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('03/01/2023');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        // AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('25/04/2023');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().should('be.empty');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        // AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().contains('-');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        // AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('250,00');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        // AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('67.392,00');
   
    }

    validaPCDevolvidaParaAcertosCT01() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        cy.wait(1000);
        AcompanhamentoPC.validaCardPCDevolvidasParaAcertos().should('be.visible');   
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.contains('Status').should('be.visible');
        cy.contains('Devolvida para acertos').should('be.visible');
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('SUZANA CAMPOS TAUIL');
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('CEI DIRET')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('900232').should('be.visible');
        AcompanhamentoPC.validaStatusPCDevolvidaParaAcertos().should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(100);
        AcompanhamentoPC.botaoMaisFiltros().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().click().type('26/04/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().click().type('19/04/2024');
        cy.focused().type('{enter}')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.contains('900232').should('be.visible');
        cy.contains('CEI DIRET SUZANA CAMPOS TAUIL').should('be.visible');
        AcompanhamentoPC.validaStatusPCDevolvidaParaAcertos().should('be.visible');
        
    }

    validaPCDevolvidaParaAcertosCT02() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('SUZANA CAMPOS TAUIL');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('Recebimento pela Diretoria').should('be.visible'); //validação campos bloqueados apenas visualização
        cy.contains('Técnico responsável').should('be.visible');
        AcompanhamentoPC.campoTecnicoResponsável().should('be.empty').should('not.be.enabled')
        cy.contains('Data de recebimento').should('be.visible');
        AcompanhamentoPC.campoDataRecebimento().should("have.value","26/04/2023").should('not.be.enabled')
        cy.contains('Status').should('be.visible');
        AcompanhamentoPC.campoStatus().contains('Devolvida para acertos').parent().should('not.be.enabled')
        cy.contains('Informativos da prestação de contas').should('be.visible'); 
        cy.contains('Processo SEI *').should('be.visible');
        AcompanhamentoPC.campoProcessoSEI().should("have.value","6016.2022/0047360-6").should('not.be.enabled')
        cy.contains('Última análise').should('be.visible');
        AcompanhamentoPC.campoUltimaAnalise().should("have.value","19/04/2024").should('not.be.enabled')

    }

    validaPCDevolvidaParaAcertosCT03() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('VEREADOR FRANCISCO PEREZ');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Materiais de referência').should('be.visible');
        cy.contains('Conta Cheque').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        cy.contains('Síntese do período de realização da despesa').should('be.visible');
        cy.contains('Data').should('be.visible');
        cy.contains('06/01/2023').should('be.visible');
        cy.contains('Saldo').should('be.visible');
        cy.contains('R$ 45.041,79').should('be.visible');
        cy.contains('Diferença em relação à prestação de contas').should('be.visible');
        cy.contains('R$ 0,00').should('be.visible');
        cy.contains('Extrato Bancário da Conta Cheque').should('be.visible');
        AcompanhamentoPC.tabelaExtratoBancario().parent().contains('Custeio (R$)');
        AcompanhamentoPC.tabelaExtratoBancario().parent().contains('Capital (R$)');
        AcompanhamentoPC.tabelaExtratoBancario().parent().contains('Livre aplicação (R$)');
        AcompanhamentoPC.tabelaExtratoBancario().parent().contains('Total (R$)');
        AcompanhamentoPC.olhoExtratoBancarioDaContaCheque().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.dowloadExtratoBancarioDaContaCheque().click();
        AcompanhamentoPC.botaoAdicionarAcerto().click({force: true});
        cy.contains('Saldo inicial (reprogramado do período anterior)').should('be.visible');
        cy.contains('Repasses').should('be.visible');
        cy.contains('Demais créditos').should('be.visible');
        cy.contains('Despesas').should('be.visible');
        cy.contains('Saldo final').should('be.visible');
        cy.contains('Despesas não demonstradas').should('be.visible');
        cy.contains('Saldo reprogramado (para o próximo período)').should('be.visible');
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        cy.wait(300)
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        cy.contains('PTRF Básico').should('be.visible');
        cy.contains('Rolê Cultural').should('be.visible');
        cy.contains('Formação').should('be.visible');
        cy.contains('Material Pedagógico').should('be.visible');
        cy.contains('Salas e Espaços de Leitura').should('be.visible');
        cy.contains('Material Complementar').should('be.visible');
        AcompanhamentoPC.subcolapse1().dblclick();
        AcompanhamentoPC.subcolapse2().dblclick();
        AcompanhamentoPC.subcolapse3().dblclick();
        AcompanhamentoPC.subcolapse4().dblclick();
        AcompanhamentoPC.subcolapse5().dblclick();
        cy.contains('Nome do arquivo').should('be.visible');
        cy.contains('Demonstrativo Financeiro da Conta Cheque').should('be.visible');
        cy.contains('Relação de Bens da Conta Cheque').should('be.visible');
        cy.contains('Ata de apresentação da prestação de conta').should('be.visible');
        cy.contains('Ata de retificação da prestação de conta').should('be.visible');
        AcompanhamentoPC.lupa1().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa2().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa3().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa4().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.baixarArquivo1().click();
        AcompanhamentoPC.baixarArquivo2().click();
        AcompanhamentoPC.baixarArquivo3().click();
        AcompanhamentoPC.baixarArquivo4().click();

    }

    validaPCDevolvidaParaAcertosCT04() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('VEREADOR FRANCISCO PEREZ');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        cy.contains('Conta Cheque').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        cy.contains('Exibindo 25 lançamentos').should('be.visible');
        cy.wait(100);
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Exibindo 23 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoMaisFiltros().click();
        AcompanhamentoPC.campoTipoDeLancamento().select('Gastos');
        AcompanhamentoPC.campoTipoDeDocumento().select('DANFE');
        AcompanhamentoPC.campoFormaDePagamento().select('DOC/TED/PIX');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Exibindo 6 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoMaisFiltros().click();
        AcompanhamentoPC.campoNumeroDeDocumento().type('402')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Exibindo 1 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(1000);
        cy.contains('Exibindo 25 lançamentos').should('be.visible');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().check();
        cy.wait(1000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('29/11/2022');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().uncheck();
        cy.wait(1000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('01/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('01/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('20/12/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().should('be.empty');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().contains('Serviço com imposto');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('11,00');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('17.000,00');
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validaCamposDetalhesTabelaConferenciaLancamentos()
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(300);
        cy.contains('CNPJ / CPF').should('not.exist');
        cy.wait(300);

    }

    validaPCDevolvidaParaAcertosCT05() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('VEREADOR FRANCISCO PEREZ');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de documentos').should('be.visible');
        cy.contains('Exibindo 7 documentos').should('be.visible');
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
        cy.get(':nth-child(1) > [style="border-right: none; width: 100px;"] > .p-2').parent().get('.svg-inline--fa.fa-circle-check ').eq('3')
        cy.get(':nth-child(3) > [style="border-right: none; width: 100px;"] > .p-2').contains('-')
        
    }

    validaPCDevolvidaParaAcertosCT06() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('VEREADOR FRANCISCO PEREZ');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Devolução para acertos')
        AcompanhamentoPC.botaoVerResumo().click();
        cy.wait(6000);
        cy.contains('Resumo de acertos');
        cy.contains('Histórico');
        cy.contains('Versão da devolução:');
        cy.contains('Data de devolução da DRE:');
        cy.contains('Prazo para reenvio:');
        cy.contains('Acertos nos lançamentos');
        cy.contains('Exibindo 7 lançamentos');
        AcompanhamentoPC.verAcertos().click();
        cy.contains('Tipo de acerto:').should('be.visible');
        cy.contains('Detalhamento:').should('be.visible');
        cy.contains('Status:').should('be.visible');
        AcompanhamentoPC.verAcertos().click();
        cy.contains('Acertos nos documentos');
        cy.contains('Exibindo 3 documentos');
        cy.contains('DRE - Relatório dos acertos');
        cy.contains('2º Relatório de devoluções para acertos');
        AcompanhamentoPC.dowloadRelatorioAcertos().click();
        cy.wait(1000);
        AcompanhamentoPC.campoVisualizeDevolucoesDatas().select('Primeira devolução 06/04/2023')
        cy.wait(8000);
        cy.contains('Acertos nas informações de extratos bancários');
        cy.contains('Acertos nos lançamentos');
        cy.contains('Exibindo 8 lançamentos');
        cy.contains('Acertos nos documentos');
        cy.contains('Exibindo 3 documentos');
        cy.contains('DRE - Relatório dos acertos');
        cy.contains('1º Relatório de devoluções para acertos');
        AcompanhamentoPC.donwloadRelatorioAcertosAnterior().click();
        cy.wait(1000);
        cy.contains('Associação - Relatório de apresentação após acertos'); 
        cy.contains('1º Relatório de apresentação após acertos');
        AcompanhamentoPC.donwloadRelatorioAposAcertos().click();
        cy.wait(1000);
        AcompanhamentoPC.campoVisualizeDevolucoesDatas().select('Segunda devolução 19/04/2024');
        cy.contains('Voltar').click();
        cy.wait(1000);
        cy.contains('Devolução para acertos');

    }

    validaPCDevolvidaParaAcertosCT07() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('CAMPOS SALLES, PRES.');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Comentários');
        cy.contains('Crie os comentários e arraste as caixas para cima ou para baixo para reorganizar. Notifique a Associação caso queira, selecionando os comentários no checkbox.');
        cy.contains('Comentários já notificados');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir comentario e cancelar inserção
        cy.wait(300);
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário01 - teste automatizado'); 
        AcompanhamentoPC.cancelarComentario().click();
        cy.wait(300);
        cy.contains('comentário01 - teste automatizado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 1
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário1 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário1 - teste automatizado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - cancelar
        cy.contains('Edição de comentário');
        cy.contains('Apagar');
        cy.contains('Salvar');
        cy.contains('Cancelar').click();
        cy.wait(300);
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - salvar
        cy.get('.modal-content > .modal-body > .row > .col-12 > .form-control').clear().type('editado');
        cy.contains('Salvar').click();
        cy.wait(300);
        cy.contains('editado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - apagar
        cy.contains('Apagar').click();// modal excluir
        cy.wait(300);
        cy.contains('Excluir Comentário');
        cy.contains('Deseja realmente excluir este comentário?');
        AcompanhamentoPC.modalExcluirComentarioCancelar().click();
        cy.wait(300);
        cy.contains('Apagar').click();
        cy.wait(300);
        AcompanhamentoPC.modalExcluirComentarioExcluir().click();
        cy.wait(300);
        cy.contains('editado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 2 
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário2 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 3
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário3 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário2 - teste automatizado');
        cy.contains('comentário3 - teste automatizado');
        AcompanhamentoPC.marcarComentarioNotificar().click({ multiple: true });
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        cy.contains('Notificar comentários');
        cy.contains('Deseja enviar os comentários selecionados como notificações para a associação?');
        cy.contains('Sim');
        AcompanhamentoPC.modalNotificarComentarioNao().click();
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        AcompanhamentoPC.modalNotificarComentarioSim().click();
        cy.wait(300);
        cy.contains('Notificado');

    }

    validaPCDevolvidaParaAcertosCT08() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('CAMPOS SALLES, PRES.');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(4000);
        cy.contains('Legenda informação');
        cy.contains('Legenda conferência');
        AcompanhamentoPC.legendaInformacaoLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validalegendaInformacaoLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaLancamentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaDocumentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaDocumentos()
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.botaoIrParaListagem().click();
        cy.contains('Materiais de referência').should('not.exist');
        cy.contains('Filtrar por um termo').should('be.visible');
    }

    validaPCApresentadaAposAcertosCT01() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        cy.wait(1000);
        AcompanhamentoPC.validaCardPCDevolvidasParaAcertos().should('be.visible');   
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.contains('Status').should('be.visible');
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('CEI DIRET')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('400082').should('be.visible');
        AcompanhamentoPC.validaStatusPCApresentadaAposAcertos().should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(100);
        AcompanhamentoPC.botaoMaisFiltros().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().click().type('13/02/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().click().type('10/05/2023');
        cy.focused().type('{enter}')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.contains('400082').should('be.visible');
        cy.contains('CEI DIRET JARDIM GUAIRACA').should('be.visible');
        AcompanhamentoPC.validaStatusPCApresentadaAposAcertos().should('be.visible');
        
    }

    validaPCApresentadaAposAcertosCT02() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('Recebimento pela Diretoria').should('be.visible'); //validação campos bloqueados apenas visualização
        cy.contains('Técnico responsável').should('be.visible');
        AcompanhamentoPC.campoTecnicoResponsável().should('be.empty').should('not.be.enabled')
        cy.contains('Data de recebimento').should('be.visible');
        AcompanhamentoPC.campoDataRecebimento().should("have.value","13/02/2023").should('not.be.enabled')
        cy.contains('Status').should('be.visible');
        AcompanhamentoPC.campoStatus().contains('Apresentada após acertos').parent().should('not.be.enabled')
        cy.contains('Informativos da prestação de contas').should('be.visible'); 
        cy.contains('Processo SEI *').should('be.visible');
        AcompanhamentoPC.campoProcessoSEI().should("have.value","6016.2022/0041004-3").should('not.be.enabled')
        cy.contains('Última análise').should('be.visible');

    }

    validaPCApresentadaAposAcertosCT03() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('Devolutiva da Associação').should('be.visible'); 
        cy.contains('Prazo de reenvio:').should('be.visible');
        cy.contains('Data de recebimento da devolutiva:').should('be.visible');
        AcompanhamentoPC.botaoReceberAposAcertos().should('not.be.enabled');
        AcompanhamentoPC.campoDataRecebimentoDevolutiva().type('06/05/2024');
        cy.focused().type('{enter}');
        AcompanhamentoPC.botaoReceberAposAcertos().click();
        cy.wait(2000);
        cy.contains('Status alterado com sucesso')
        cy.contains('A prestação de conta foi alterada para “Recebida após acertos”.')
        cy.wait(3000);
        AcompanhamentoPC.campoStatus().contains('Recebida após acertos').parent().should('not.be.enabled')
        AcompanhamentoPC.botaoApresentadaAposAcertos().click();
        cy.wait(2000);
        cy.contains('Status alterado com sucesso')
        cy.contains('A prestação de conta foi alterada para “Apresentada após acertos”.')
        cy.wait(3000);
        AcompanhamentoPC.campoStatus().contains('Apresentada após acertos').parent().should('not.be.enabled')
        
    }

    validaPCApresentadaAposAcertosCT04() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Materiais de referência').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        AcompanhamentoPC.validaSintesePeriodoRealizacaoDespesa()
        cy.wait(1000);
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        cy.wait(300)
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        AcompanhamentoPC.validaSintesePeriodoPorAcao()
        cy.wait(1000);
        AcompanhamentoPC.subcolapse1().dblclick();
        AcompanhamentoPC.subcolapse2().dblclick();
        AcompanhamentoPC.subcolapse3().dblclick();
        AcompanhamentoPC.subcolapse4().dblclick();
        AcompanhamentoPC.subcolapse5().dblclick();
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        cy.wait(100);
        AcompanhamentoPC.validaNomeDoArquivo()
        AcompanhamentoPC.lupa1().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa2().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa3().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa4().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.baixarArquivo1().click();
        AcompanhamentoPC.baixarArquivo2().click();
        AcompanhamentoPC.baixarArquivo3().click();
        AcompanhamentoPC.baixarArquivo4().click();
    } 

    validaPCApresentadaAposAcertosCT05() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de lançamentos').should('be.visible');
        cy.contains('Conta Cheque').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        cy.contains('Exibindo 58 lançamentos').should('be.visible');
        cy.wait(100);
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Exibindo 58 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoMaisFiltros().click();
        AcompanhamentoPC.campoTipoDeLancamento().select('Gastos');
        AcompanhamentoPC.campoTipoDeDocumento().select('Extrato');
        AcompanhamentoPC.campoFormaDePagamento().select('Débito em conta');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(2000);
        cy.contains('Exibindo 26 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(2000);
        cy.contains('Exibindo 58 lançamentos').should('be.visible');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().check();
        cy.wait(2000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('06/09/2022');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().uncheck();
        cy.wait(2000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('06/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('06/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('30/12/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().should('be.empty');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().contains('Conciliada');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('2,65');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('16.220,00');
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validaCamposDetalhesTabelaConferenciaLancamentos()
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(300);
        cy.contains('CNPJ / CPF').should('not.exist');
        cy.wait(300);

    } 

    validaPCApresentadaAposAcertosCT06() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de documentos').should('be.visible');
        cy.contains('Exibindo 7 documentos').should('be.visible');
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
        cy.get(':nth-child(1) > [style="border-right: none; width: 100px;"] > .p-2').parent().get('.svg-inline--fa.fa-circle-check ').eq('6')
        cy.get(':nth-child(2) > [style="border-right: none; width: 100px;"] > .p-2').parent().get('.svg-inline--fa.fa-circle-check ').eq('1')
        
    }

    validaPCApresentadaAposAcertosCT07() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Devolução para acertos')
        AcompanhamentoPC.botaoDevolverParaAssociacao().should('not.be.enabled');
        AcompanhamentoPC.botaoVerResumo().click();
        cy.wait(6000);
        cy.contains('Resumo de acertos');
        cy.contains('Histórico');
        cy.contains('Versão da devolução:');
        cy.contains('Data de devolução da DRE:');
        cy.contains('Prazo para reenvio:');
        cy.contains('Data de devolução da UE:');
        cy.contains('Acertos nos lançamentos');
        cy.contains('Exibindo 14 lançamentos');
        AcompanhamentoPC.verAcertos().click();
        cy.contains('Tipo de acerto:').should('be.visible');
        cy.contains('Detalhamento:').should('be.visible');
        cy.contains('Status:').should('be.visible');
        AcompanhamentoPC.verAcertos().click();
        AcompanhamentoPC.pagina2LancamentosResumo().click();
        cy.wait(100);
        cy.contains('Acertos nos documentos');
        cy.contains('Exibindo 6 documentos');
        AcompanhamentoPC.pagina2DocumentosResumo().click();
        cy.wait(100);
        cy.contains('DRE - Relatório dos acertos');
        cy.contains('1º Relatório de devoluções para acertos');
        AcompanhamentoPC.dowloadRelatorioAcertos().click( { multiple: true } );
        cy.wait(1000);
        cy.contains('Associação - Relatório de apresentação após acertos'); 
        cy.contains('1º Relatório de apresentação após acertos');
        AcompanhamentoPC.dowloadRelatorioAcertos().click( { multiple: true } );
        cy.wait(1000);
        cy.contains('Voltar').click();
        cy.wait(1000);
        cy.contains('Devolução para acertos');

    }

    validaPCApresentadaAposAcertosCT08() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('IRINEU MARINHO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Comentários');
        cy.contains('Crie os comentários e arraste as caixas para cima ou para baixo para reorganizar. Notifique a Associação caso queira, selecionando os comentários no checkbox.');
        cy.contains('Comentários já notificados');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir comentario e cancelar inserção
        cy.wait(300);
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário01 - teste automatizado'); 
        AcompanhamentoPC.cancelarComentario().click();
        cy.wait(300);
        cy.contains('comentário01 - teste automatizado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 1
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário1 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário1 - teste automatizado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - cancelar
        cy.contains('Edição de comentário');
        cy.contains('Apagar');
        cy.contains('Salvar');
        cy.contains('Cancelar').click();
        cy.wait(300);
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - salvar
        cy.get('.modal-content > .modal-body > .row > .col-12 > .form-control').clear().type('editado');
        cy.contains('Salvar').click();
        cy.wait(300);
        cy.contains('editado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - apagar
        cy.contains('Apagar').click();// modal excluir
        cy.wait(300);
        cy.contains('Excluir Comentário');
        cy.contains('Deseja realmente excluir este comentário?');
        AcompanhamentoPC.modalExcluirComentarioCancelar().click();
        cy.wait(300);
        cy.contains('Apagar').click();
        cy.wait(300);
        AcompanhamentoPC.modalExcluirComentarioExcluir().click();
        cy.wait(300);
        cy.contains('editado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 2 
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário2 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 3
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário3 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário2 - teste automatizado');
        cy.contains('comentário3 - teste automatizado');
        AcompanhamentoPC.marcarComentarioNotificar().click({ multiple: true });
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        cy.contains('Notificar comentários');
        cy.contains('Deseja enviar os comentários selecionados como notificações para a associação?');
        cy.contains('Sim');
        AcompanhamentoPC.modalNotificarComentarioNao().click();
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        AcompanhamentoPC.modalNotificarComentarioSim().click();
        cy.wait(300);
        cy.contains('Notificado');

    }

    validaPCApresentadaAposAcertosCT09() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('JARDIM GUAIRACA');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(3000);
        cy.contains('Legenda informação');
        cy.contains('Legenda conferência');
        AcompanhamentoPC.legendaInformacaoLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validalegendaInformacaoLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaLancamentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaDocumentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaDocumentos()
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.botaoIrParaListagem().click();
        cy.contains('Materiais de referência').should('not.exist');
        cy.contains('Filtrar por um termo').should('be.visible');
    }

    validaPCRecebidaAposAcertosCT01() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');
        cy.wait(1000);
        AcompanhamentoPC.validaCardPCDevolvidasParaAcertos().should('be.visible');   
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.campoFiltrarPorTipoDeUnidade().select('EMEI')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('091898').should('be.visible');
        cy.contains('EMEI ALCEU MAYNARD DE ARAUJO, PROF.').should('be.visible');
        AcompanhamentoPC.validaStatusPCRecebidaAposAcertos().contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(100);
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.deletarfiltros().click();
        AcompanhamentoPC.campoFiltrarPorStatus().click()
        AcompanhamentoPC.selecionarRecebidaAposAcertos().click();
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoMaisFiltros().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorPeriodoInicio().click().type('13/02/2023');
        AcompanhamentoPC.campoFiltrarPorPeriodoFim().click().type('23/03/2023');
        cy.focused().type('{enter}')
        AcompanhamentoPC.botaoFiltrar().click();
        cy.contains('091898').should('be.visible');
        cy.contains('EMEI ALCEU MAYNARD DE ARAUJO, PROF.').should('be.visible');
        AcompanhamentoPC.validaStatusPCRecebidaAposAcertos().contains('Recebida após acertos').should('be.visible');
    }

    validaPCRecebidaAposAcertosCT02() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(2000);
        cy.contains('APM EMEI PROFESSOR ALCEU MAYNARD DE ARAUJO').should('be.visible');
        cy.contains('Recebimento pela Diretoria').should('be.visible'); //validação campos bloqueados apenas visualização
        cy.contains('Técnico responsável').should('be.visible');
        AcompanhamentoPC.campoTecnicoResponsável().should('be.empty').should('not.be.enabled')
        cy.contains('Data de recebimento').should('be.visible');
        AcompanhamentoPC.campoDataRecebimento().should("have.value","13/02/2023").should('not.be.enabled')
        cy.contains('Status').should('be.visible');
        AcompanhamentoPC.campoStatus().contains('Recebida após acertos').parent().should('not.be.enabled')
        cy.contains('Devolutiva da Associação').should('be.visible'); 
        cy.contains('Prazo de reenvio: 30/03/2023').should('be.visible');
        cy.contains('Data de recebimento da devolutiva:').should('be.visible');
        AcompanhamentoPC.campoDataRecebimentoDevolutiva().should("have.value","30/05/2024").should('not.be.enabled')
        cy.contains('Informativos da prestação de contas').should('be.visible'); 
        cy.contains('Processo SEI *').should('be.visible');
        AcompanhamentoPC.campoProcessoSEI().should("have.value","6016.2022/0041106-6").should('not.be.enabled')
        cy.contains('Última análise').should('be.visible');
        
    }

    validaPCRecebidaAposAcertosCT03() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Materiais de referência').should('be.visible');
        cy.contains('Conta Cheque').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        cy.contains('Síntese do período de realização da despesa').should('be.visible');
        cy.contains('Síntese do período por ação').should('be.visible');
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        AcompanhamentoPC.validaSintesePeriodoRealizacaoDespesaRecebidaAposAcertos();
        AcompanhamentoPC.botaoAdicionarAcerto().should('not.be.enabled')
        cy.wait(100);
        AcompanhamentoPC.colapseSinteseDoPeriodoDeRealizacaoDaDespesa().click();
        cy.wait(300)
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        AcompanhamentoPC.validaSintesePeriodoPorAcao()
        cy.wait(1000);
        AcompanhamentoPC.subcolapse1().dblclick();
        AcompanhamentoPC.subcolapse2().dblclick();
        AcompanhamentoPC.subcolapse3().dblclick();
        AcompanhamentoPC.subcolapse4().dblclick();
        AcompanhamentoPC.subcolapse5().dblclick();
        AcompanhamentoPC.subcolapse6().dblclick();
        AcompanhamentoPC.colapseSinteseDoPeriodoPorAcao().click();
        cy.wait(100);
        AcompanhamentoPC.validaNomeDoArquivo()
        AcompanhamentoPC.lupa1().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa2().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa3().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.lupa4().click();
        AcompanhamentoPC.Xmodal().click();
        AcompanhamentoPC.baixarArquivo1().click();
        AcompanhamentoPC.baixarArquivo2().click();
        AcompanhamentoPC.baixarArquivo3().click();
        AcompanhamentoPC.baixarArquivo4().click();
    } 

    validaPCRecebidaAposAcertosCT04() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('APM EMEI PROFESSOR ALCEU MAYNARD DE ARAUJO').should('be.visible');
        cy.contains('Recebida após acertos').should('be.visible');
        cy.contains('Conferência de lançamentos').should('be.visible');
        cy.contains('Conta Cheque').should('be.visible');
        cy.contains('Conta Cartão').should('be.visible');
        cy.contains('Exibindo 34 lançamentos').should('be.visible');
        cy.wait(100);
        AcompanhamentoPC.campoAcao().select('PTRF Básico');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Exibindo 31 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoMaisFiltros().click();
        AcompanhamentoPC.campoTipoDeLancamento().select('Gastos');
        AcompanhamentoPC.campoTipoDeDocumento().select('Extrato');
        AcompanhamentoPC.campoFormaDePagamento().select('Débito em conta');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(2000);
        cy.contains('Exibindo 16 lançamentos').should('be.visible');
        AcompanhamentoPC.botaoLimpar().click();
        cy.wait(2000);
        cy.contains('Exibindo 34 lançamentos').should('be.visible');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().check();
        cy.wait(2000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('02/09/2022');
        AcompanhamentoPC.checkboxOrdenarComImpostoVinculadosAsDespesas().uncheck();
        cy.wait(2000);
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('02/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('02/09/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosDataOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaDataOrdenacao().contains('30/12/2022');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().should('be.empty');
        AcompanhamentoPC.colunaConferenciaDeLancamentosInformacoesOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaInformacoesOrdenacao().contains('Conciliada');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('2,65');
        AcompanhamentoPC.colunaConferenciaDeLancamentosValorOrdenacao().click();
        AcompanhamentoPC.validaCampoTabelaValorOrdenacao().contains('10.183,00');
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validaCamposDetalhesTabelaConferenciaLancamentos()
        AcompanhamentoPC.expandirTabelaConferenciaDeLancamentos().click();
        cy.wait(300);
        cy.contains('CNPJ / CPF').should('not.exist');
        cy.wait(300);

    } 

    validaPCRecebidaAposAcertosCT05() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Conferência de documentos').should('be.visible');
        cy.contains('Exibindo 7 documentos').should('be.visible');
        AcompanhamentoPC.validaConferenciaDocumentos()
        cy.get(':nth-child(1) > [style="border-right: none; width: 100px;"] > .p-2').parent().get('.svg-inline--fa.fa-circle-check ').eq('6')
        cy.get(':nth-child(2) > [style="border-right: none; width: 100px;"] > .p-2').parent().get('.svg-inline--fa.fa-circle-check ').eq('1')
        
    }

    validaPCRecebidaAposAcertosCT06() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        cy.contains('Devolução para acertos')
        AcompanhamentoPC.campoPrazoParaReenvio().should('not.be.enabled');
        AcompanhamentoPC.botaoDevolverParaAssociacao().should('not.be.enabled');
        AcompanhamentoPC.botaoVerResumo().click();
        cy.wait(6000);
        cy.contains('APM EMEI PROFESSOR ALCEU MAYNARD DE ARAUJO');
        AcompanhamentoPC.validaVerResumoDeAcertos()
        AcompanhamentoPC.verAcertos().click();
        cy.contains('Tipo de acerto:').should('be.visible');
        cy.contains('Enviar o documento comprobatório da despesa')
        cy.contains('Detalhamento:').should('be.visible');
        cy.contains('Inserir no processo SEI a Nota Fiscal da despesa com obrigações acessórias, comprovante de pagamento e orçamentos.').should('be.visible');
        cy.contains('Status:').should('be.visible');
        AcompanhamentoPC.verAcertos().click();
        AcompanhamentoPC.pagina2LancamentosResumo().click();
        cy.wait(100);
        cy.contains('Acertos nos documentos');
        cy.contains('Exibindo 2 documentos');
        cy.contains('DRE - Relatório dos acertos');
        cy.contains('1º Relatório de devoluções para acertos');
        AcompanhamentoPC.dowloadRelatorioAcertos().click( { multiple: true } );
        cy.wait(1000);
        cy.contains('Associação - Relatório de apresentação após acertos'); 
        cy.contains('1º Relatório de apresentação após acertos');
        AcompanhamentoPC.dowloadRelatorioAcertos().click( { multiple: true } );
        cy.wait(1000);
        cy.contains('Voltar').click();
        cy.wait(1000);
        cy.contains('Devolução para acertos');

    }

    validaPCRecebidaAposAcertosCT07() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('AUREA RIBEIRO XAVIER LOPES');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(1000);
        cy.contains('Comentários');
        cy.contains('Crie os comentários e arraste as caixas para cima ou para baixo para reorganizar. Notifique a Associação caso queira, selecionando os comentários no checkbox.');
        cy.contains('Comentários já notificados');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir comentario e cancelar inserção
        cy.wait(300);
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário01 - teste automatizado'); 
        AcompanhamentoPC.cancelarComentario().click();
        cy.wait(300);
        cy.contains('comentário01 - teste automatizado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 1
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário1 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário1 - teste automatizado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - cancelar
        cy.contains('Edição de comentário');
        cy.contains('Apagar');
        cy.contains('Salvar');
        cy.contains('Cancelar').click();
        cy.wait(300);
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - salvar
        cy.get('.modal-content > .modal-body > .row > .col-12 > .form-control').clear().type('editado');
        cy.contains('Salvar').click();
        cy.wait(300);
        cy.contains('editado');
        AcompanhamentoPC.editarComentario().click(); // editar comentario - modal - apagar
        cy.contains('Apagar').click();// modal excluir
        cy.wait(300);
        cy.contains('Excluir Comentário');
        cy.contains('Deseja realmente excluir este comentário?');
        AcompanhamentoPC.modalExcluirComentarioCancelar().click();
        cy.wait(300);
        cy.contains('Apagar').click();
        cy.wait(300);
        AcompanhamentoPC.modalExcluirComentarioExcluir().click();
        cy.wait(300);
        cy.contains('editado').should('not.exist');
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 2 
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário2 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        AcompanhamentoPC.botaoAdicionarNovoComentario().click(); // inserir novo comentario 3
        AcompanhamentoPC.inserirTextoCaixaComentario().type('comentário3 - teste automatizado');
        AcompanhamentoPC.botaoConfirmarComentario().click();
        cy.wait(300);
        cy.contains('comentário2 - teste automatizado');
        cy.contains('comentário3 - teste automatizado');
        AcompanhamentoPC.marcarComentarioNotificar().click({ multiple: true });
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        cy.contains('Notificar comentários');
        cy.contains('Deseja enviar os comentários selecionados como notificações para a associação?');
        cy.contains('Sim');
        AcompanhamentoPC.modalNotificarComentarioNao().click();
        AcompanhamentoPC.botaoNotificarAssociacao().click();
        AcompanhamentoPC.modalNotificarComentarioSim().click();
        cy.wait(300);
        cy.contains('Notificado');

    }

    validaPCRecebidaAposAcertosCT08() {
        AcompanhamentoPC.botaoPeriodos().select('2022.3 - 01/09/2022 até 31/12/2022');       
        AcompanhamentoPC.botaoVerPretacoes4card().click();
        cy.wait(1000);
        AcompanhamentoPC.campoFiltrarPorUmTermo().type('AUREA RIBEIRO XAVIER LOPES');
        AcompanhamentoPC.botaoFiltrar().click();
        cy.wait(1000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoAcoes().click();
        cy.wait(3000);
        cy.contains('Legenda informação');
        cy.contains('Legenda conferência');
        AcompanhamentoPC.legendaInformacaoLancamentos().click();
        cy.wait(1000);
        AcompanhamentoPC.validalegendaInformacaoLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaLancamentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaLancamentos();
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.legendaConferenciaDocumentos().click()
        cy.wait(1000);
        AcompanhamentoPC.validalegendaConferenciaDocumentos()
        AcompanhamentoPC.botaoFecharLegenda().click();
        AcompanhamentoPC.botaoApresentadaAposAcertos().click();
        cy.wait(300);
        cy.contains('Status alterado com sucesso').should('be.visible');
        cy.contains('A prestação de conta foi alterada para “Apresentada após acertos”.').should('be.visible');
        cy.wait(3000);
        cy.contains('Apresentada após acertos').should('be.visible');
        AcompanhamentoPC.campoDataRecebimentoDevolutiva().click().type('27/05/2024');
        AcompanhamentoPC.botaoReceberAposAcertos().click();
        cy.wait(300);
        cy.contains('Status alterado com sucesso').should('be.visible');
        cy.contains('A prestação de conta foi alterada para “Recebida após acertos”.').should('be.visible');
        cy.wait(3000);
        cy.contains('Recebida após acertos').should('be.visible');
        AcompanhamentoPC.botaoIrParaListagem().click();
        cy.contains('Materiais de referência').should('not.exist');
        cy.contains('Filtrar por um termo').should('be.visible');
        cy.contains('Recebida após acertos').should('be.visible');
    }



}

export default AcompanhamentoPcPagina;

