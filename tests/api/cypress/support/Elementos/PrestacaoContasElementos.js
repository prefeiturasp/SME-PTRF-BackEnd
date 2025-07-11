class PrestacaoContasElementos {

    //----------------------- Geração de Documentos -------------------------\\    
    periodo = () => { return cy.get('#periodoPrestacaoDeConta')};
    botaoPrevia = () => { return cy.get('.actions > .btn').contains('prévia')};
    botaoPreviaRelacaoBens = () => { return cy.get(':nth-child(5) > article > .actions > .btn').contains('prévia')};
    demonstrativoFinanceiro = () => { return cy.get(':nth-child(4) > article > .info > .fonte-14 > strong').contains('Demonstrativo Financeiro da Conta')};
    bensAdquiridos = () => { return cy.get(':nth-child(5) > article > .info > .fonte-14 > strong').contains('Bens adquiridos ou produzidos')};
    ataApresentacao = () => { return cy.get('.col-md-8 > .fonte-14 > strong').contains('Ata de Apresentação da prestação de contas')};
    botaoGerarPrevia = () => { return cy.get('.modal-footer > .btn-success').contains('Gerar Prévia')};
    botaoCancelarPrevia = () => { return cy.get('.modal-footer > .btn-outline-success').contains('Gerar Prévia')};
    botaoVisualizarPreviaAta = () => { return cy.get('.col-md-4 > .btn').contains('Visualizar prévia da ata')};
    botaoEditarAta = () => { return cy.get('.btn-success').contains('Editar ata')};
    botaoFecharAta = () => { return cy.get('.btn-outline-success > strong').contains('Fechar')};
    botaoSalvarEdicaoAta = () => { return cy.get('.btn-success > strong').contains('Salvar edições')};
    botaoVoltarParaAta = () => { return cy.get('.btn-success > strong').contains('Voltar para ata')};
    botaoAdicionarPresente = () => { return cy.get('.d-flex > .btn').contains('+ Adicionar presente')};
    botaoConfirmarPresente = () => { return cy.get(':nth-child(19) > .form-row > .col-2').contains('Confirmar')};
    botaoConcluirPeriodo = () => { return cy.get('.col-lg-5 > .btn').contains('Concluir período')};
    botaoConcluirPrestacaoConfirmar = () => { return cy.get('.modal-footer > .btn-success').contains('Confirmar')};
    botaoFecharDocumentoGerado = () => { return cy.get('[data-qa]').contains('Fechar')};
    botaoDownloadPdf = () => { return cy.get('.btn-editar-membro')};

    //----------------------- Geração de Documentos - Edição da Ata-------------------------\\  
    campoIdentificador = () => { return cy.get(':nth-child(19) > .form-row > :nth-child(1)')};
    campoNome = () => { return cy.get(':nth-child(19) > .form-row > .col-4')};
    campoCargo = () => { return cy.get(':nth-child(19) > .form-row > :nth-child(3)')};
    
}

export default PrestacaoContasElementos;