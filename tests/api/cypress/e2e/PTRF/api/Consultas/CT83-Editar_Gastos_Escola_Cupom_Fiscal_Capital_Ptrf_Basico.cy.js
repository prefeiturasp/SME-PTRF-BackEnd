///<reference types="cypress" />

// Fixture (3 níveis acima)
import usuarios from "../../../../fixtures/usuariosPTRF.json";
const usuario = usuarios.Kellen;

// Páginas (3 níveis acima)
import ComumPaginaPTRF from "../../../../support/Paginas/ComumPaginaPTRF";
const Comum = new ComumPaginaPTRF();

import GastosEscolaPagina from "../../../../support/Paginas/GastosEscolaPagina";
const Gastos = new GastosEscolaPagina();

Cypress.on('uncaught:exception', (err, runnable) => {
  // quando retorna falso previne o Cypress de falhar o teste
  return false;
});

describe('Gastos da Escola - Editar', () => {

  it('CT83-Editar_Gastos_Escola_Cupom_Fiscal_Capital_Ptrf_Basico', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();
    Gastos.selecionarFiltrarMaisFiltros(); 
    Gastos.selecionarAplicacaoCusteio();

    Comum.selecionarPerfil();
    Comum.logout();
  });

  it('CT235-Editar_Gastos_Escola_Acesso_Tela_Gastos', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();
    Gastos.selecionarGastosDaEscola();

    Comum.logout();
  });

  it('CT236-Editar_Gastos_Escola_Aplicar_Filtro_Custeio', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();
    Gastos.selecionarFiltrarMaisFiltros();
    Gastos.selecionarAplicacaoCusteio();

    Comum.logout();
  });

  it('CT237-Editar_Gastos_Escola_Reaplicar_Filtros', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();
    Gastos.selecionarFiltrarMaisFiltros();
    Gastos.selecionarAplicacaoCusteio();
    Gastos.selecionarAplicacaoCusteio();

    Comum.logout();
  });

  it('CT238-Editar_Gastos_Escola_Troca_Perfil_Apos_Filtro', () => {

    Comum.visitarPaginaPTRF();
    Comum.login(usuario.Usuario, usuario.Senha);

    Comum.selecionarCeuVilaAlpina();

    Gastos.selecionarGastosDaEscola();
    Gastos.selecionarFiltrarMaisFiltros();
    Gastos.selecionarAplicacaoCusteio();

    Comum.selecionarPerfil();
    Comum.logout();
  });

});
