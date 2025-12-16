///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();
  describe('Gastos da Escola - Consulta', () => {

    it('CT79-Consulta_Gastos_Escola_Atividade_Programa',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();

    Gastos.selecionarFiltrarMaisFiltros(); 
    
    Gastos.selecionarAplicacaoCusteio();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})