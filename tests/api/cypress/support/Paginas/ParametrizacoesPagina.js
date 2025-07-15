//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Parametros = new ComumElementosPTRF

import PeriodoElementos from "../Elementos/PeriodoElementos"
const Periodo = new PeriodoElementos

class ParametrizacoesPagina {

    selecionarParametrizacoes() {
        Parametros.menuParametrizacoes().click();
    }

    selecionarPeriodo() {
        Periodo.botaoPeriodo().click();
    }

    adcionarPeriodo() {
        Periodo.botaoAdcionarPeriodo().click();
        Periodo.adcionarReferencia().type('2023.1');
        Periodo.adcionarData().type('19/05/2023');
        Periodo.adcionarInicioDespesas().type('01/01/2023');
        Periodo.adcionarFimDespesas().type('06/01/2023');
        Periodo.adcionarInicioContas().type('16/01/2023');
        Periodo.adcionarFimContas().type('19/01/2023');
        Periodo.adcionarPeriodoAnterior().select('2022.3 - 01/09/2022 até 31/12/2022');
    }

    editarPeriodo() {
        Periodo.botaoEditar().click({froce:true});
    }

    realizaPesquisaPeriodo() {
        Periodo.pesquisarPerido().type('2023');
    }

    filtrarPeriodo() {
        Periodo.botaoFiltar().click();
    }

    limparPesquisaPeriodo() {
        Periodo.botaoLimpar().click();
    }

    salvarAdcionarPeriodo() {
        Periodo.botaoSalvar().click();
    }

    cancelarAdcionarPeriodo() {
        Periodo.botaoCancelar().click();
    }

    apagarPeriodo() {
        Periodo.botaoApagar().click();
    }

    modalExluirPeriodo() {
        Periodo.botaoExcluir().click();
    }

    cancelarModalPeriodo() {
        Periodo.botaoCancelarModalExcluir().click();
    }
    
    
}

export default ParametrizacoesPagina;

