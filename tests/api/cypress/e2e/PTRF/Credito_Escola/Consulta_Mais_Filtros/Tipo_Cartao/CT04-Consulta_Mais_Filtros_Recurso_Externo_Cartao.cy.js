//<reference types="cypress" />

import usuarios from "../../../../../fixtures/usuariosPTRF.json"
const usuario = usuarios.Kellen

import ComumPaginaPTRF from "../../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF

import CreditosEscolaPagina from "../../../../../support/Paginas/CreditosEscolaPagina"
const Creditos = new CreditosEscolaPagina


Cypress.on('uncaught:exception', (err, runnable) => {
    // quando retorna falso previne o  Cypress de falhar o teste
    return false
  })

  describe('Credito Escola - Consulta - Mais Filtros - Tipo_Cartao', () => {

    it('CT04-Consulta_Mais_Filtros_Recurso_Externo_Cheque',()=>{

    Comum.visitarPaginaPTRF();

    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Creditos.selecionarCreditosDaEscola();

    Creditos.selecionarMaisFiltros();

    Creditos.selecionarRecursoExternoMaisFiltros();

    Creditos.selecionarDetalhamentoMaisFiltros();

    Creditos.realizaConsultaTipoContaCartao();

    Creditos.realizaConsultaAcaoPtrf();

    Creditos.realizaConsultaDataInicio();

    Creditos.realizaConsultaDataFim();

    Creditos.selecionarFiltrarMaisFiltros();
    
    Comum.selecionarPerfil();

    Comum.logout();
    
  })  

})