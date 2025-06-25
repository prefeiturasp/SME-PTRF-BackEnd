//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Parametros = new ComumElementosPTRF

import CreditosEscolaElementos from "../Elementos/CreditosEscolaElementos"
const Creditos = new CreditosEscolaElementos

import { format } from "../Elementos/UtilsCreditosEscolaElementos"


class CreditosEscolaPagina {

    selecionarCreditosDaEscola() {
        Parametros.menuCreditosDaEscola().click();
    }

    selecionarArredondamento() {
        Creditos.arredondamento().should('be.visible');
    }

    selecionarArredondamentoMaisFiltros() {
        Creditos.arredondamentoMaisFiltros().should('be.visible');
    }

    selecionarDevolacaoConta() {
        Creditos.devolucaoConta().should('be.visible');
    }

    selecionarDevolacaoContaMaisFiltros() {
        Creditos.devolucaoContaMaisFiltros().should('be.visible');
    }

    selecionarEstorno() {
        Creditos.estorno().should('be.visible');
    }

    selecionarEstornoMaisFiltos() {
        Creditos.estornoMaisFiltros().should('be.visible');
    }

    selecionarRecursoExterno() {
        Creditos.recursoExterno().should('be.visible');
    }

    selecionarRecursoExternoMaisFiltros() {
        Creditos.recursoExternoMaisFiltros().should('be.visible');
    }

    selecionarRendimento() {
        Creditos.rendimento().should('be.visible');
        cy.wait(3000);
    }

    selecionarRendimentoMaisFiltros() {
        Creditos.rendimentoMaisFiltros().should('be.visible');
        cy.wait(3000);
    }

    selecionarRepasse() {
        Creditos.repasse().should('be.visible');
    }

    selecionarRepasseMaisFiltros() {
        Creditos.repasseMaisFiltros().should('be.visible');
    }

    selecionarDetalhamentoMaisFiltros() {
        Creditos.selecionarDetalhamentoCreditoMaisFiltros().type('Junho');
    }    


    validarCreditosCadastrados() {
        Creditos.validarTipo().should('be.visible');
        Creditos.validarConta().should('be.visible');
        Creditos.validarAcao().should('be.visible');
        Creditos.validarData().should('be.visible');
        Creditos.validarValor().should('be.visible');
    }


    realizarCadastroCredito() {
        cy.wait(3000);
        Creditos.selecionarReceitaRendimento().should('be.visible');    
        Creditos.selecionarDetalhamentoCredito().should('be.visible');
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        Creditos.selecionarTipoContaCheque().should('be.visible');
        Creditos.selecionarAcaoPtrf().should('be.visible');
        Creditos.selecionarClassificacaoCreditoCusteio().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorTotalCredito().type('1000000');
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click();

    }

    realizarCadastroCreditoRendimentoCusteioCheque() {
        cy.wait(3000);
        Creditos.selecionarReceitaRendimento().should('be.visible');    
        Creditos.selecionarDetalhamentoCredito().should('be.visible');
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        Creditos.selecionarTipoContaCheque().should('be.visible');
        Creditos.selecionarAcaoPtrf().should('be.visible');
        Creditos.selecionarClassificacaoCreditoCusteio().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorTotalCredito().type('100000');
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click();

    }


    realizarCadastroCreditoRendimentoLivreAplicacaoCheque() {
        cy.wait(3000);
        Creditos.selecionarReceitaRendimento().should('be.visible');    
        Creditos.selecionarDetalhamentoCredito().should('be.visible');
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        Creditos.selecionarTipoContaCheque().should('be.visible');
        Creditos.selecionarAcaoPtrf().should('be.visible');
        Creditos.selecionarClassificacaoCreditoLivreAplicacao().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorTotalCredito().type('100000');
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click();

    }

    realizarCadastroCreditoRepasseValorCapital() {
        cy.wait(3000);
        Creditos.selecionarReceitaRepasse().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorCapital().click();
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        cy.wait(3000);
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoNaoCancelarRepasse().click();
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoGravarRepasse().click();

    }


    realizarCadastroCreditoRepasseValorCusteio() {
        cy.wait(3000);
        Creditos.selecionarReceitaRepasse().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorCusteio().click();
        cy.wait(3000);
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        cy.wait(3000);
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoNaoCancelarRepasse().click();
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoGravarRepasse().click();

    }
    

    realizarCadastroCreditoRepasseValorLivreAplicacao() {
        cy.wait(3000);
        Creditos.selecionarReceitaRepasse().should('be.visible');
        cy.wait(3000);
        Creditos.selecionarValorLivreAplicacao().click();
        cy.wait(3000);
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('1').click();
        cy.wait(3000);
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoNaoCancelarRepasse().click();
        // Creditos.botaoSalvarCadastroCredito().click();
        // Creditos.botaoGravarRepasse().click();

    }


    realizarCadastroCreditoRendimentoCamposEmBranco() {
        cy.wait(3000);
        Creditos.selecionarReceitaRendimento().should('be.visible');
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click({force: true});
        cy.wait(3000);
        Creditos.validaDetalhamento().should('be.visible');
        Creditos.validaDataCredito().should('be.visible');
        Creditos.validaTipoConta().should('be.visible');
        Creditos.validaAcaoSelecionada().should('be.visible');
        Creditos.validaClassificacaoSelecionada().should('be.visible');
        Creditos.validaCampoValor().should('be.visible');
        cy.wait(3000);

    }


    realizarEdicaoCadastroCredito() {
        Creditos.editarRendimento().click();
        Creditos.selecionarReceitaRendimento().should('be.visible');    
        Creditos.selecionarDetalhamentoCredito().should('be.visible');
        Creditos.selecionarDataCredito().clear().type('28/07/2023');
        Creditos.selecionarTipoContaCheque().should('be.visible');
        Creditos.selecionarAcaoPtrf().should('be.visible');
        Creditos.selecionarClassificacaoCreditoCusteio().should('be.visible');
        Creditos.selecionarValorTotalCredito().clear().type('1200000');
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click();
        cy.wait(5000);

    }

    realizarEdicaoRendimentoRepasse() {
        Creditos.editarRendimento().click();
        Creditos.selecionarReceitaRendimento().should('be.visible');
        Creditos.selecionarReceitaRepasse().should('be.visible');
        Creditos.selecionarValorLivreAplicacao().click();
        Creditos.botaoSalvarCadastroCredito().click();
        cy.wait(3000);
        Creditos.botaoNaoCancelarRepasse().click();
        cy.wait(3000);

    }

    realizarEdicaoRepasse() {
        Creditos.editarRepasse().click();
        Creditos.selecionarDataCredito().click();
        cy.wait(3000);
        Creditos.selecionarDataCreditoCalendario().contains('16').click();
        Creditos.botaoSalvarCadastroCredito().click();
        cy.wait(3000);
        Creditos.botaoNaoCancelarRepasse().click();
        cy.wait(3000);
        Creditos.botaoSalvarCadastroCredito().click();
        Creditos.botaoGravarRepasse().click();

    }

    realizaConsultaDetalhamentoCredito() { 
        Creditos.selecionarDetalhamentoCredito().should('be.visible');
    }

    realizaConsultaTipoContaCheque() { 
        Creditos.selecionarTipoContaCheque().should('be.visible');
    }

    realizaConsultaTipoContaCartao() { 
        Creditos.selecionarTipoContaCartao().should('be.visible');
    }


    realizaConsultaAcaoPtrf() { 
        Creditos.selecionarAcaoPtrf().should('be.visible');
    }
    
    realizaConsultaAcaoSalas() { 
        Creditos.selecionarAcaoSalas().should('be.visible');
    }
    
    realizaConsultaAcaoMaterialPedagogico() { 
        Creditos.selecionarAcaoMaterialPedagogico().should('be.visible');
    }

    realizaConsultaAcaoRecurso() { 
        Creditos.selecionarAcaoRecurso().should('be.visible');
    }

    realizaConsultaAcaoMaterialComplementar() { 
        Creditos.selecionarAcaoMaterialComplementar().should('be.visible');
    }

    realizaConsultaDataInicio() { 
        Creditos.selecionarDataIncio().type('01/01/2023');
    }

    realizaConsultaDataFim() { 
        Creditos.selecionarDataFim().type('30/07/2023');
    }

    filtrarReceita() {
        Creditos.botaoFiltrarReceita().click();
        cy.wait(3000)
    }

    selecionarMaisFiltros() {
        Creditos.botaoMaisFiltros().click();
    }

    selecionarFiltrarMaisFiltros() {
        Creditos.validarSemFiltroAplicado().click();
        Creditos.botaoFiltrarMaisFiltros().click();
        cy.wait(3000)
    }

    selecionarCancelar() {
        Creditos.validarSemFiltroAplicado().click();
        Creditos.botaoCancelar().click();
    }

    selecionarLimparFiltros() {
        Creditos.validarSemFiltroAplicado().click();
        Creditos.botaoLimparFiltros().click();
    }

    selecionarCadastrarCredito() {
        Creditos.botaoCadastrarCredito().click();
    }

    selecionarValoresReprogramados() {
        Creditos.botaoValoresReprogramados().click();
    }

    validarRetornoSemResultado() {
        Creditos.semResultado().should('be.visible');
    }



    validarSoma() {
        let valor = 0

        Creditos.validarTabelaValor().each(($el, index, $list) => {cy.log(index)});
        Creditos.validarTabelaValor()
            .each(($el, index, $list) => {
                Creditos.recebeValor($el)
                    .invoke('text').then((text) => {
                        cy.log(text)
                        if(text.includes('-')){
                            valor = valor + format(text)
                            cy.log(valor)
                        }
                    })
            });


        Creditos.validarTabelaValor().each(($el, index, $list) => {cy.log(index)});
        Creditos.avancarPaginas().click();
        Creditos.validarTabelaValor()
            .each(($el, index, $list) => {
                Creditos.recebeValor($el)
                    .invoke('text').then((text) => {
                        if(text.includes('-')){
                            valor = valor + format(text)

                        }
                        cy.log(valor)
                    })
            });

        Creditos.validarTabelaValor().each(($el, index, $list) => {cy.log(index)});
        Creditos.avancarPaginas().click();
        Creditos.validarTabelaValor()
            .each(($el, index, $list) => {
                Creditos.recebeValor($el)
                    .invoke('text').then((text) => {
                        if(text.includes('-')){
                            valor = valor + format(text)

                        }
                        cy.log(valor)
                    })
            });

        Creditos.validarValorTotalFiltroAplicado().invoke('text').then(text => {
            let valorTotal = 0;
            const valorEsperado = 21794.47;

            valorTotal += isNaN(valor) ? 0 : valor;

            expect(valorTotal).to.equal(valorEsperado)
        })

    }
    




}

export default CreditosEscolaPagina;