//reference types="Cypress" />

import ComumElementosPTRF from "../Elementos/ComumElementosPTRF"
const Parametros = new ComumElementosPTRF

import ResumoElementos from "../Elementos/ResumoElementos";
const Resumo = new ResumoElementos

class ResumoPagina {

    selecionarPeriodo() {
        Resumo.periodoAtual().should('be.visible');
        
    }    

    selecionarResumo() {
        Parametros.menuResumoDosRecursos().click();
    }

    selecionarTodasContas() {
        Resumo.todasContas().should('be.visible');
    }

    selecionarTipoCartao() {
        Resumo.tipoCartao().should('be.visible');
    }

    selecionarTipoCheque() {
        Resumo.tipoCheque().should('be.visible');
        cy.get('.col-md-5 > :nth-child(3)').should('be.visible');
        cy.get('.col-md-5 > .mb-0').should('be.visible');
        cy.get('.row > :nth-child(2) > .pt-0 > :nth-child(1)').should('be.visible');
    }

    
}

export default ResumoPagina;

