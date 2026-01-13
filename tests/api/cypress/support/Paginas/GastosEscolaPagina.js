//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Parametros = new ComumElementosPTRF

import GastosEscolaElementos from "../Elementos/GastosEscolaElementos";
const Gastos = new GastosEscolaElementos


class GastosEscolaPagina {

    selecionarGastosDaEscola() {
        Parametros.menuGastosDaEscola().click();
    }

    selecionarFiltrarMaisFiltros() {
        Gastos.botaoMaisFiltros().click();
        cy.wait(3000);
    }

    selecionarPeriodoFechado() {
        Gastos.periodoMaisFiltros().should('be.visible');
        Gastos.periodoMaisFiltros().click();
        Gastos.dataInicioPeriodoMaisFiltros().type('08/06/2022');
        Gastos.calendarioMaisFiltros().contains('01').click();
        Gastos.dataFimPeriodoMaisFiltros().type('31/08/2022');
        Gastos.calendarioMaisFiltros().contains('31').click();
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().click();
        cy.wait(3000);
        Gastos.botaoFechar().click();
        cy.wait(3000);
        Gastos.botaoVoltar().click();
        cy.wait(3000);
    }


    selecionarPeriodoAberto() {
        Gastos.resultadoGridMaisFiltos().click();
        cy.wait(3000);
        Gastos.botaoVoltar().click();
        cy.wait(3000);
    }


    selecionarEspecificacaoExistente() {
        Gastos.especificacaoMaisFiltros().type('Material');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
    }


    selecionarEspecificacaoInexistente() {
        Gastos.especificacaoMaisFiltros().type('Mterial');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
    }


    selecionarAplicacaoCapital() {
        Gastos.aplicacaoCapitalMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        cy.wait(3000);
    }


    selecionarAplicacaoCusteio() {
        Gastos.aplicacaoCusteioMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        cy.wait(3000);
    }

    selecionarAcaoPtrf() {
        Gastos.acaoPtrfMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        cy.wait(3000);
    }

    selecionarAcaoSalas() {
        Gastos.acaoSalasMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        cy.wait(3000);
    }

    selecionarAcaoMaterialPedagogico() {
        Gastos.acaoMaterialPedagogicoMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        cy.wait(3000);
    }

    selecionarAcaoRecurso(retornoMensagem) {
        Gastos.acaoRecursoMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarAcaoMaterialComplemetar(retornoMensagem) {
        Gastos.acaoMaterialComplementarMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }

    selecionarInformacaoAntecipado(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoAntecipadoMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }

    selecionarInformacaoEstornado(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoEstornadoMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }
    

    selecionarInformacaoParcial(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoParcialMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }
    

    selecionarInformacaoImposto(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoImpostoMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarInformacaoImpostoPago(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoImpostoPagoMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }
    

    selecionarInformacaoExcluido(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoExcluidoMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarInformacaoNaoReconhecida(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoNaoReconhecidaMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }
    

    selecionarInformacaoSemComprovacaoFiscal(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoSemComprovacaoFiscalMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }
    

    selecionarInformacaoConciliada(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoConciliadaMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarInformacaoNaoConciliada(retornoMensagem) {
        Gastos.informacacaoMaisFiltros().click();
        Gastos.informacacaoConciliadaMaisFiltros().should('be.visible').click();
        Gastos.informacacaoNaoConciliadaMaisFiltros().should('be.visible').click();
        Gastos.informacacaoConciliadaMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.informacacaoMaisFiltros().click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarContaCheque(retornoMensagem) {
        Gastos.contaChequeMaisFiltros().should('be.visible');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarContaCartao(retornoMensagem) {
        Gastos.contaCartaoMaisFiltros().should('be.visible');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarStatusCompleto(retornoMensagem) {
        Gastos.statusCompletoMaisFiltros().should('be.visible');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarStatusRascunho(retornoMensagem) {
        Gastos.statusRascunhoMaisFiltros().should('be.visible');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }

    selecionarAtividadeCovid(retornoMensagem) {
        Gastos.atividadeMaisFiltros().click();
        Gastos.atividadeCovidMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarAtividadePrograma(retornoMensagem) {
        Gastos.atividadeMaisFiltros().click();
        Gastos.atividadeProgramaMaisFiltros().should('be.visible').click();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarFornecedor(retornoMensagem) {
        Gastos.fornecedorMaisFiltros().type('BIGNARDI IND');
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarFiltroCombinadoExistente(retornoMensagem) {
        Gastos.especificacaoMaisFiltros().type('Material');
        cy.wait(3000);
        Gastos.aplicacaoCapitalMaisFiltros();
        cy.wait(3000);
        Gastos.acaoPtrfMaisFiltros();
        cy.wait(3000);
        Gastos.contaChequeMaisFiltros();
        cy.wait(3000);
        Gastos.statusCompletoMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        cy.wait(3000);
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }


    selecionarFiltroCombinadoInexistente(retornoMensagem) {
        Gastos.especificacaoMaisFiltros().type('Material');
        cy.wait(3000);
        Gastos.aplicacaoCusteioMaisFiltros();
        cy.wait(3000);
        Gastos.acaoPtrfMaisFiltros();
        cy.wait(3000);
        Gastos.contaCartaoMaisFiltros();
        cy.wait(3000);
        Gastos.statusRascunhoMaisFiltros();
        cy.wait(3000);
        Gastos.periodoMaisFiltros().should('be.visible');
        Gastos.periodoMaisFiltros().click();
        Gastos.dataInicioPeriodoMaisFiltros().type('01/06/2023');
        Gastos.calendarioMaisFiltros().contains('01').click();
        Gastos.dataFimPeriodoMaisFiltros().type('15/08/2023');
        Gastos.calendarioMaisFiltros().contains('15').click();
        Gastos.botaoFiltrar().click();
        cy.wait(3000);
        if (retornoMensagem) {
            Gastos.resultadoGridMaisFiltos().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        if (retornoMensagem) {
            Gastos.filtroSemResultado().scrollIntoView({ block: 'center' }).should('be.visible');
        }
        cy.wait(3000);
    }

    //----------------------- Cadastrado de Despesa -------------------------\\

    selecionarCadastrarDespesa() {
        Gastos.botaoCadastrarDespesa().click();
        cy.wait(3000);
    }

    validarCadastroDespesaComprovanteGeneroAlimenticioPtrf_Basico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
    }

    validarCadastroDespesaComprovanteGeneroAlimenticioSalasEspacosLeitura() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        Gastos.cadastroTipoDespesaCusteio().select('Gênero alimentício');
        Gastos.cadastroEspecificacaoCusteio().select('Dieta especial');
        Gastos.cadastroAcaoCusteio().select('Salas e Espaços de Leitura');
        Gastos.cadastroTipoContaCusteio().select('Cheque');
        Gastos.cadastroValorCusteio().type('100000');
        Gastos.cadastroPossiuVinculo().click();
        Gastos.cadastroAtividadeVinculada().select('COVID-19');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();        
    }

    validarCadastroDespesaComprovanteImpostoMaterialPedagogico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
        // Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        // Gastos.cadastroTipoDespesaCusteio().select('Imposto');
        // Gastos.cadastroEspecificacaoCusteio().select('PIS/COFINS/CSLL');
        // Gastos.cadastroAcaoCusteio().select('Material Pedagógico');
        // Gastos.cadastroTipoContaCusteio().select('Cartão');
        // //Gastos.cadastroValorCusteio().type('100000');      
    }

    validarCadastroDespesaComprovanteTributosTarifasMaterialComplementar() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaComprovanteTransferenciaContasBbCusteioIncompletoSim() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.wait(3000);
        Gastos.botaoModalDespesaSim().click();
    }

    validarCadastroDespesaComprovanteTransferenciaContasBbCusteioIncompletoNao() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.wait(3000);
        Gastos.botaoModalDespesaNao().click();
        cy.wait(3000);
    }

    validarCadastroDespesaComprovanteCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaComprovanteCapitalSalasEspacosLeitura() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaComprovanteCapitalMaterialPedagogico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroTipoAplicacaoRecurso().select('Capital');
        Gastos.botaoEstouCiente().should('be.visible').click();
        Gastos.cadastroEspecificacaoCapital().select('Amplificador');
        Gastos.cadastroAcaoCapital().select('Material Pedagógico');
        //Gastos.cadastroTipoContaCapital().select('Cartão');
        // Gastos.cadastroPossiuVinculo().click();
        // Gastos.cadastroAtividadeVinculada().select('Programa de Cuidados com as Estudantes');
        // cy.wait(3000);
        // Gastos.botaoSalvarCadastroDespesa().click();
        // Gastos.botaoModalTipoAplicacaoNao().click();
        // cy.wait(3000);
        // Gastos.botaoVoltarCadastroDespesa().click();
        // cy.wait(3000);
        // Gastos.botaoModalCancelarCadastroOk().click();        
    }

    validarCadastroDespesaComprovanteCapitalMaterialComplementar() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('2000');
        // Gastos.cadastroTipoAplicacaoRecurso().select('Capital');
        // Gastos.botaoEstouCiente().should('be.visible').click();
        // Gastos.cadastroEspecificacaoCapital().select('Caneta para gravacao');
        // Gastos.cadastroAcaoCapital().select('Material Complementar');
        // Gastos.cadastroQuantidadeItensCapital().type('1');       
    }

    validarCadastroDespesaCupomFiscalCusteioGeneroAlimenticioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaCupomFiscalCusteioGeneroAlimenticioSalasEspacosLeitura() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaCupomFiscalImpostoMaterialPedagogico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroNumeroCheque().type('54515451');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
        // Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        // Gastos.cadastroTipoDespesaCusteio().select('Imposto');
        // Gastos.cadastroEspecificacaoCusteio().select('PIS/COFINS/CSLL');
        // Gastos.cadastroAcaoCusteio().select('Material Pedagógico');
        // Gastos.cadastroTipoContaCusteio().select('Cartão');
        // Gastos.cadastroValorCusteio().type('100000');
        // Gastos.cadastroPossiuVinculo().click();
        // Gastos.cadastroAtividadeVinculada().select('Programa de Cuidados com as Estudantes');
        // cy.wait(3000);
        // Gastos.botaoSalvarCadastroDespesa().click();
        // cy.get('[data-qa="modal-saldo-insuficiente-conta-btn-Fechar"]').click()
        // cy.wait(3000); 
        // cy.get('[data-qa="cadastro-edicao-despesa-btn-salvar"]').click() 
    }

    validarCadastroDespesaCupomFiscalTributosTarifasMaterialComplementar() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');    
    }

    validarCadastroDespesaCupomFiscalTransferenciaContasBbCusteioIncompletoSim() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
    }

    validarCadastroDespesaCupomFiscalTransferenciaContasBbCusteioIncompletoNao() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
    }

    validarCadastroDespesaCupomFiscalCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaCupomFiscalCapitalSalasEspacosLeitura() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroDespesaCupomFiscalCapitalMaterialPedagogico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');     
    }

    validarCadastroDespesaCupomFiscalCapitalMaterialComplementar() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('Cupom fiscal');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');         
    }

    realizaEdicaoGastosEscolaCupomFiscalCapitalPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.aplicacaoCapitalMaisFiltros();
        Gastos.acaoPtrfMaisFiltros();
        cy.wait(3000);
        Gastos.contaChequeMaisFiltros();
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.get('[data-qa="modal-despesa-incompleta-btn-Sim"]').click()
    }

    realizaEdicaoGastosEscolaCupomFiscalCapitalSalasEspacosLeitura() {
        Gastos.botaoMaisFiltros().click();
        Gastos.aplicacaoCapitalMaisFiltros();
        Gastos.acaoSalasMaisFiltros();
        Gastos.contaChequeMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.get('[data-qa="modal-despesa-incompleta-btn-Sim"]').click()
    }

    realizaEdicaoGastosEscolaCupomFiscalCusteioMaterialPedagogico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.aplicacaoCusteioMaisFiltros();
        Gastos.acaoMaterialPedagogicoMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.get('[data-qa="modal-despesa-incompleta-btn-Sim"]').click()
    }

    realizaEdicaoGastosEscolaCupomFiscalCusteioMaterialComplementar() {
        Gastos.botaoMaisFiltros().click();
        Gastos.aplicacaoCusteioMaisFiltros();
        Gastos.acaoMaterialComplementarMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.botaoSalvarCadastroDespesa().click();
        cy.get('[data-qa="modal-despesa-incompleta-btn-Sim"]').click()
    }

    realizaEdicaoFiltrosCombinadosExistentes() {
        Gastos.botaoMaisFiltros().click();
        Gastos.aplicacaoCusteioMaisFiltros();
        Gastos.acaoMaterialComplementarMaisFiltros();
        cy.wait(3000);
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        Gastos.cadastroTipoDocumento().select('Comprovante');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('30/08/2023');
        Gastos.cadastroFormaPagamento().select('Transferência entre contas BB');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('30/08/2023');
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
        Gastos.cadastroTipoAplicacaoRecurso().select('Capital');
        Gastos.botaoEstouCiente().should('be.visible').click();
        Gastos.cadastroEspecificacaoCapital().select('Caneta para gravacao');
        Gastos.cadastroAcaoCapital().select('Material Complementar');
        Gastos.cadastroQuantidadeItensCapital().type('1');
        Gastos.cadastroProcessoCapital().type('1313131313131313');
        Gastos.cadastroTipoContaCapital().select('Cheque');
        Gastos.cadastroNaoPossiuVinculo().click();
        Gastos.botaoSalvarCadastroDespesa().click();
        Gastos.botaoModalTipoAplicacaoNao().click();
        cy.wait(3000);
        Gastos.botaoVoltarCadastroDespesa().click();
        cy.wait(3000);
        Gastos.botaoModalCancelarCadastroOk().click(); 
    }

    validarCadastroGastosEscolaDanfeCartaoCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaDespesaReconhecidaAssociacaoSimCartaoCusteioPtrfBasico() {
        Gastos.naoPossuiComprovacaoFiscal().click();
        Gastos.despesaReconhecida().click();
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaDanfeChequeCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroNumeroCheque().type('312963274727411095009241501056');
        // Gastos.cadastroValorTotalDocumento().type('200000');
        // Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaDanfeDocCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('DOC/TED/PIX');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseCartaoCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414250');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseChequeCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroNumeroCheque().type('312963274727411095009241501056');
        // Gastos.cadastroValorTotalDocumento().type('200000');
        // Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseDocCusteioPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414251');
        Gastos.cadastroFormaPagamento().select('DOC/TED/PIX');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
        // Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        // Gastos.cadastroTipoDespesaCusteio().select('Serviço');
        // Gastos.cadastroEspecificacaoCusteio().select('Jardinagem');
        // Gastos.cadastroAcaoCusteio().select('PTRF Básico');
        // Gastos.cadastroTipoContaCusteio().select('Cartão');
        // Gastos.cadastroValorCusteio().type('100000');
        // Gastos.cadastroPossiuVinculo().click(); 
        // Gastos.cadastroAtividadeVinculada().select('COVID-19');
        // cy.wait(3000);
        // Gastos.botaoSalvarCadastroDespesa().click();
        // cy.get('[data-qa="modal-saldo-insuficiente-conta-btn-Fechar"]').click()
        // // Gastos.botaoDespesaCastradaSim().click();
    }

    validarCadastroGastosEscolaDanfeCartaoCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaDanfeChequeCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414251');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroNumeroCheque().type('312963274727411095009241501056');
        // Gastos.cadastroValorTotalDocumento().type('200000');
        // Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaDanfeDocCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414243');
        Gastos.cadastroFormaPagamento().select('DOC/TED/PIX');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseCartaoCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414254');
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseChequeCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414255');
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroNumeroCheque().type('312963274727411095009241501056');
        // Gastos.cadastroValorTotalDocumento().type('200000');
        // Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaNfseDocCapitalPtrfBasico() {
        Gastos.cadastroFornecedor().type('007.461.987-01');
        Gastos.cadastroRazaoSocialFornecedor().type('Teste');
        Gastos.cadastroTipoDocumento().select('NFS-e');
        Gastos.cadastroDataDocumento().click();
        Gastos.cadastroDataDocumento().type('15/08/2023');
        Gastos.cadastroNumeroDocumento().type('414256');
        Gastos.cadastroFormaPagamento().select('DOC/TED/PIX');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaIncompletoBoletimOcorrenciaNaoPreenchido() {
        Gastos.naoPossuiComprovacaoFiscal().click();
        Gastos.despesaNaoReconhecida().click();
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroDataPagamento().click();
        Gastos.cadastroDataPagamento().type('28/08/2023');
        Gastos.calendarioMaisFiltros().contains('28').click();
        Gastos.cadastroValorTotalDocumento().type('200000');
        Gastos.cadastroValorRecursoProprio().type('100000');
    }

    validarCadastroGastosEscolaIncompletoDanfeChequeContinuarPreenchendoCamposSim() {
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroFormaPagamento().select('Cheque');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
        Gastos.botaoModalDespesaSim().click();
    }

    validarCadastroGastosEscolaIncompletoDanfeChequeContinuarPreenchendoCamposNao() {
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroFormaPagamento().select('Cheque');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
        Gastos.botaoModalDespesaNao().click();
    }

    realizaEdicaoGastosEscolaDanfeCusteioPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Certificado Digital');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.cadastroFormaPagamento().select('Cartão');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
    }

    realizaEdicaoGastosEscolaDanfeDocCusteioPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Certificado Digital');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.naoPossuiComprovacaoFiscal().click();
        Gastos.despesaNaoReconhecida().click();
        Gastos.cadastroFormaPagamento().select('DOC/TED/PIX');
        Gastos.cadastroBoletimOcorrencia().type('0123456789');
        Gastos.cadastroDadosGasto().select('Sim');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        cy.wait(3000);
        Gastos.cadastroValorCusteio().clear().type('90000');
        Gastos.cadastroNaoPossiuVinculo().click();
        Gastos.botaoAdicionarDespesaParcial().click();
        cy.wait(3000);
        Gastos.cadastroTipoAplicacaoDespesa2().select('Custeio');
        Gastos.cadastroAcaoCusteio2().select('PTRF Básico');
        Gastos.cadastroTipoContaCusteio2().select('Cartão');
        Gastos.cadastroValorCusteio2().clear().type('10000');
        Gastos.botaoSalvarCadastroDespesa().click();
    }

    realizaEdicaoGastosEscolaNfseChequeCusteioPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Jardinagem');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.possuiComprovacaoFiscal().click();
        cy.wait(3000);
        Gastos.cadastroValorRecursoProprio().clear().type('180000');
        Gastos.despesaRetemImposto().click();
        Gastos.botaoAdicionarImposto().click();
        Gastos.cadastroEdicaoImpostoDocumento().select('DARF');
        Gastos.cadastroEdicaoEspecificacaoImposto().select('PIS/COFINS/CSLL');
        Gastos.cadastroEdicaoImpostoFormaPagamento().select('Cartão');
        Gastos.cadastroEdicaoDataPagamentoImposto().clear().type('29/09/2023');
        Gastos.cadastroEdicaoDespesaAcaoImposto().select('PTRF Básico');
        Gastos.cadastroEdicaoTipoContaImposto().select('Cartão');
        Gastos.cadastroEdicaoValorImposto().clear().type('10000');
        Gastos.cadastroTipoContaCusteio().select('Cheque');
        Gastos.cadastroValorCusteio().clear().type('10000');
        cy.wait(3000);
        Gastos.botaoSalvarCadastroDespesa().click();
    }

    realizaEdicaoGastosEscolaDanfeChequeCusteioPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Certificado Digital');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.cadastroFormaPagamento().select('Cheque');
        Gastos.cadastroNumeroCheque().type('312963274727411095009241501056');
        Gastos.cadastroTipoAplicacaoRecurso().select('Custeio');
        cy.wait(3000);
        Gastos.cadastroNaoPossiuVinculo().click();
        Gastos.botaoSalvarCadastroDespesa().click();
    }

    realizaEdicaoGastosEscolaDanfeCartaoCapitalPtrfBasico() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Aparelho celular');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.cadastroTipoDocumento().select('DANFE');
        Gastos.cadastroAtividadeVinculada().select('COVID-19');
        Gastos.botaoSalvarCadastroDespesa().click();
    }

    realizaEdicaoGastosEscolaCadastroEstornoCampoObrigatorio() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Aparelho celular');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);
        Gastos.cadastrarEstorno().click();
        cy.wait(3000);
        Gastos.botaoSalvar().click();
        Gastos.campoObrigatorioCadastroEstorno().should('be.visible');
    }

    realizaEdicaoGastosEscolaCadastroEstornoSalvarData() {
        Gastos.botaoMaisFiltros().click();
        Gastos.especificacaoMaisFiltros().type('Aparelho celular');
        Gastos.botaoFiltrar().click();
        Gastos.numeroDocumentoGrid().click();
        cy.wait(3000);       
        Gastos.cadastrarEstorno().click();
        Gastos.dataCadastroEstorno().type('30/09/2023');
        Gastos.calendarioEstorno().contains('30').click();
        cy.wait(3000); 
        Gastos.botaoSalvar().click();
        Gastos.dataCadastroEstorno().type('30/09/2023');
        Gastos.calendarioEstorno().contains('30').click();
        // cy.wait(3000);  
        // Gastos.motivosEstorno().click();
        // Gastos.tarifaBancaria().click();
        // Gastos.fecharMotivosEstorno().click();
        // Gastos.confirmarMotivosEstorno().click();
    }


}

export default GastosEscolaPagina;

