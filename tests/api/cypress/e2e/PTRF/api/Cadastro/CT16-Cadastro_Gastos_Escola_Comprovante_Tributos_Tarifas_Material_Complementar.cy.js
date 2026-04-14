///<reference types="cypress" />

import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF"
const Comum = new ComumPaginaPTRF()

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina"
const Gastos = new GastosEscolaPagina()

describe("Gastos da Escola - Cadastro", () => {

  it("CT16-Cadastro_Gastos_Escola_Comprovante_Tributos_Tarifas_Material_Complementar", () => {
    
    Comum.visitarPaginaPTRF()

    cy.realizar_login('UE')

    Gastos.selecionarGastosDaEscola()  

    Gastos.selecionarCadastrarDespesa()

    Gastos.validarCadastroDespesaComprovanteTributosTarifasMaterialComplementar()
    
    Comum.selecionarPerfil()

    Comum.logout()
  })
})
