class ResumoElementos {

    //-----------------------Selecionar Período-------------------------\\
    periodoAtual = () => { return cy.get('[class="form-control"]').eq(2)};



    //--------------------------Tipo de Conta----------------------------\\

    todasContas = () => { return cy.get(':nth-child(4) > #periodo').select("Todas as contas")};
    tipoCartao = () => { return cy.get(':nth-child(4) > #periodo').select('Cartão')};
    tipoCheque = () => { return cy.get(':nth-child(4) > #periodo').select("Cheque")};

    

}

export default ResumoElementos;