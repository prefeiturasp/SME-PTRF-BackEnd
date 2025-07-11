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


const tempoEspera = 5000;

Cypress.Commands.add('login', (RF, password) => { 
    //Login
    cy.visit('https://test-conf-novosgp.sme.prefeitura.sp.gov.br'); // https://hom-novosgp.sme.prefeitura.sp.gov.br
    cy.wait(1000);
    cy.get('[id="usuario"]',{timeout:tempoEspera}).type(RF);
    cy.get('[id="senha"]',{timeout:tempoEspera}).type(password);
   // cy.contains('Acessar').click()
    cy.wait(2000);
})

Cypress.Commands.add('selecionarItemMenuLateral', (item, subItem) => { 

    cy.get('[id=menuPrincipal]',{timeout:tempoEspera}).contains(item).click();
    cy.get('[role=menuitem]',{timeout:tempoEspera}).contains(subItem).parent().click({});
})



Cypress.Commands.add('trocarPerfil', (perfil) => { 

    cy.get('[class = "list-inline p-0 m-0"]').click()
    cy.get('[class ="sc-gJTSre fAgxqv list-inline"]').contains(perfil).click({})
    cy.wait(tempoEspera);
    cy.get('[class = "list-inline p-0 m-0"]').click()
})


Cypress.Commands.add('SelecionarTurmaFiltroPrincipal', (historico,valores) => { 
    // filtro principal de turma
    cy.get('[class*= "rounded-circle"]',{timeout:tempoEspera}).click()
    if(historico){
            cy.get('[type = checkbox]').click()
    }

    cy.wait(100)

    if(valores.ano){
        cy.contains('Ano').click()
        cy.contains(valores.ano).click()
    } 

    cy.wait(100)

    if(valores.modalidade){
        cy.contains('Modalidade').click()
        cy.contains(valores.modalidade).click()
    } 
    cy.wait(100)

    if(valores.dre){
        cy.contains('Diretoria Regional De Educação (DRE)').click()
        cy.contains(valores.dre).click()
    } 

    cy.wait(100)

    if(valores.ue){
        cy.contains('Unidade Escolar (UE)').click()
        cy.contains(valores.ue).click()
    } 

    cy.wait(100)

    if(valores.turma){
        //cy.contains('Turma').click()
        cy.get('#sgp-select-filtro-principal-turma').click()
        cy.contains(valores.turma).click()
    } 

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