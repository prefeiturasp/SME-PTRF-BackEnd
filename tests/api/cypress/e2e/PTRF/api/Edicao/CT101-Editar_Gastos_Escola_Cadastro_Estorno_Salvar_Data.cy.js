///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

describe('Gastos da Escola - Editar', () => {

    it('CT101-Editar_Gastos_Escola_Cadastro_Estorno_Salvar_Data',()=>{

    Comum.visitarPaginaPTRF();

    cy.realizar_login('UE')
    
  }) 
})