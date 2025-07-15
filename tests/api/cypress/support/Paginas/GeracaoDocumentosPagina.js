//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Comum = new ComumElementosPTRF

import PrestacaoContasElementos from "../Elementos/PrestacaoContasElementos";
const PCGeracaoDocumentos = new PrestacaoContasElementos


class GeracaoDocumentosPagina {

    selecionarPrestacaoContas() {
        Comum.menuPrestacaoContas().click();
    }

    selecionarGeracaoDocumentos() {
        Comum.menuGeracaoDocumentos().click();
    }

    realizarDemonstrativoFinanceiroPrevia() {
        PCGeracaoDocumentos.periodo().select('2023.1 - 01/01/2023 até 30/04/2023');
        PCGeracaoDocumentos.demonstrativoFinanceiro().should('be.visible');
        PCGeracaoDocumentos.botaoPrevia().click();
        PCGeracaoDocumentos.botaoGerarPrevia().click();
        cy.wait(3000);
        PCGeracaoDocumentos.botaoFecharDocumentoGerado().click();
        cy.wait(3000);
        // PCGeracaoDocumentos.botaoDownloadPdf().click();
        // cy.wait(5000);
    }

    realizarRelacaoBensAdquiridosOuProduzidosPrevia() {
        PCGeracaoDocumentos.periodo().select('2023.1 - 01/01/2023 até 30/04/2023');
        PCGeracaoDocumentos.bensAdquiridos().should('be.visible');
        PCGeracaoDocumentos.botaoPreviaRelacaoBens().click();
        PCGeracaoDocumentos.botaoGerarPrevia().click();
        cy.wait(3000);
        PCGeracaoDocumentos.botaoFecharDocumentoGerado().click();
        cy.wait(3000);
        // PCGeracaoDocumentos.botaoDownloadPdf().click();
        // cy.wait(5000);
    }

    realizarAtasPrestacaoContasPrevia() {
        PCGeracaoDocumentos.periodo().select('2023.1 - 01/01/2023 até 30/04/2023');
        PCGeracaoDocumentos.ataApresentacao().should('be.visible');
        PCGeracaoDocumentos.botaoVisualizarPreviaAta().click();
        cy.wait(8000);
        PCGeracaoDocumentos.botaoEditarAta().click();
        cy.wait(8000);
        PCGeracaoDocumentos.botaoAdicionarPresente().click();
        cy.wait(8000);
        PCGeracaoDocumentos.campoIdentificador().should('be.visible').click().type('7907664');
        PCGeracaoDocumentos.campoNome().click();
        PCGeracaoDocumentos.campoCargo().click();
        PCGeracaoDocumentos.botaoConfirmarPresente().click();
        PCGeracaoDocumentos.botaoSalvarEdicaoAta().click();
        PCGeracaoDocumentos.botaoVoltarParaAta().click();
        PCGeracaoDocumentos.botaoFecharAta().click();
    }

    realizarConcluirPeriodo() {
        PCGeracaoDocumentos.periodo().select('2023.2 - 01/05/2023 até -');
        PCGeracaoDocumentos.botaoConcluirPeriodo().click();
        PCGeracaoDocumentos.botaoConcluirPrestacaoConfirmar().click();
        
    }
    
}

export default GeracaoDocumentosPagina;

