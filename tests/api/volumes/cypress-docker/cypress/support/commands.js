// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })

const tempoEspera = 4000;

Cypress.Commands.add('login', (RF, password) => { 
    //Login
    cy.visit('https://test-conf-novosgp.sme.prefeitura.sp.gov.br/login');
    cy.wait(1000);
    cy.get('[id="usuario"]',{timeout:tempoEspera}).type(RF);
    cy.get('[id="senha"]',{timeout:tempoEspera}).type(password);
    cy.wait(2000);
})

Cypress.Commands.add('selecionarItemMenuLateral', (item, subItem) => { 

    '[id ]'

    cy.get('[id=menuPrincipal]',{timeout:tempoEspera}).contains(item).click();
    cy.get(100)
    cy.get('[role=menuitem]',{timeout:tempoEspera}).contains(subItem).parent().click({});
})

Cypress.Commands.add('FiltroTelaListão', (historico, valores) => { 
    if(historico){
            cy.get('[type = checkbox').click()
    }

    if(valores.ano){
        cy.contains('Ano',{timeout:tempoEspera}).click()
        cy.contains(valores.ano).click()
    } 

    if(valores.dre){
        cy.contains('Selecione uma DRE',{timeout:tempoEspera}).click();
        cy.contains(valores.dre).click();
    } 

    if(valores.ue){
        cy.contains('Selecione uma UE',{timeout:tempoEspera}).click();
        cy.contains(valores.ue).click();
    } 

    if(valores.modalidade){
        cy.contains('Selecione a modalidade',{timeout:tempoEspera}).click();
        cy.contains(valores.modalidade).click();
    } 

    if(valores.turma){
        cy.contains('Todas',{timeout:tempoEspera}).click()
        cy.contains(valores.turma).click()
    } 

    if(valores.bimestre){
        cy.contains('Selecione o bimestre',{timeout:tempoEspera}).click()
        cy.contains(valores.bimestre).click()
    } 

})

Cypress.Commands.add('trocarPerfil', (perfil) => { 

    cy.get('[class = "list-inline p-0 m-0"]').click()
    cy.get('[class ="sc-gJTSre fAgxqv list-inline"]').contains(perfil).click({})
    cy.wait(tempoEspera);
    cy.get('[class = "list-inline p-0 m-0"]').click()
})

Cypress.Commands.add('SelecionarTurmaFiltroPrincipal', (historico,valores) => { 
    cy.get('[class*= "rounded-circle"]',{timeout:tempoEspera}).click()
    if(historico){
            cy.get('[type = checkbox').click()
    }

    cy.wait(1000)

    if(valores.ano){
        cy.contains('Ano').click()
        cy.contains(valores.ano).click()
    } 

    if(valores.modalidade){
        cy.contains('Modalidade').click()
        cy.contains(valores.modalidade).click()
    } 

    if(valores.dre){
        cy.contains('Diretoria Regional De Educação (DRE)').click()
        cy.contains(valores.dre).click()
    } 

    if(valores.ue){
        cy.contains('Unidade Escolar (UE)').click()
        cy.contains(valores.ue).click()
    } 

    if(valores.turma){
        cy.contains('Turma').click()
        cy.contains(valores.turma).click()
    } 

    cy.wait(500);
    cy.contains('Aplicar filtro').click()

 })

//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })