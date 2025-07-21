class PeriodoElementos {

    //-----------------------Período-------------------------\\

    botaoPeriodo = () => { return cy.get('.container-cards-dre-dashboard').contains('Períodos')};

    //-----------------------Adicionar Período-------------------------\\
    botaoAdcionarPeriodo = () => { return cy.get('button.btn-success').contains('Adicionar período')};
    adcionarReferencia = () => { return cy.get('#referencia')};
    adcionarData = () => { return cy.get('input[name="data_prevista_repasse"]')};
    adcionarInicioDespesas = () => { return cy.get('input[name="data_inicio_realizacao_despesas"]')};
    adcionarFimDespesas = () => { return cy.get('input[name="data_fim_realizacao_despesas"]')};
    adcionarInicioContas = () => { return cy.get('input[name="data_inicio_prestacao_contas"]')};
    adcionarFimContas = () => { return cy.get('input[name="data_fim_prestacao_contas"]')};
    adcionarPeriodoAnterior = () => { return cy.get('#periodo_anterior')};

    //-----------------------Botões Tela Adicionar e Editar Período-------------------------\\
    botaoSalvar = () => { return cy.get('.btn-success').contains('Salvar')};
    botaoCancelar = () => { return cy.get('.btn-outline-success').contains('Cancelar')};
    botaoApagar = () => { return cy.get('.btn-danger').contains('Apagar')};
    botaoExcluir = () => { return cy.get('.btn-danger').contains('Excluir')};
    botaoCancelarModalExcluir = () => { return cy.get('.modal-footer > .btn-outline-success').contains('Cancelar')};    

    //-----------------------Editar Período-------------------------\\
    botaoEditar = () => { return cy.get('.btn-editar-membro').eq(0)};


    //-----------------------Pesquisar Período-------------------------\\
    pesquisarPerido = () => { return cy.get('#filtrar_por_referencia')};
    botaoFiltar = () => { return cy.get('.btn-success').contains('Filtrar')};
    botaoLimpar = () => { return cy.get('.btn-outline-success').contains('Limpar')};

    

    


}

export default PeriodoElementos;