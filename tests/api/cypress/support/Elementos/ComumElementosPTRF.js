class ComumElementosPTRF {
  //-----------------------LOGIN-------------------------\\
  textoUsuario = () => {
    return cy.get('[id="login"]');
  };
  textoSenha = () => {
    return cy.get('[id="senha"]');
  };
  botaoAcessar = () => {
    return cy.contains("Acessar");
  };
  botaoEsqueciSenha = () => {
    return cy.contains("Esqueci minha senha");
  };

  //-----------------------Cabeçalho PTRF-------------------------\\
  //---------------Filtro Principal-------------\\
  botaoFiltroPrincipal = () => {
    return cy
      .get(".form-control")
      .contains("SME - Secretaria Municipal de Educação");
  };
  selecaoEMEF = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("EMEF - 22 DE MARCO");
  };
  selecaoCeuVilaAlpina = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU CEMEI - VILA ALPINA");
  };
  selecaoEMEFTESTE = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("EMEF - 22 DE MARCO (TESTE)");
  };
  selecaoCeuEmefMariaClara = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU EMEF - MARIA CLARA MACHADO");
  };
  selecaoCeuEmefMarioFittipaldi = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU EMEF - MARIO FITTIPALDI");
  };
  selecaoCEUCEI = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU CEI - CANTOS DO AMANHECER)");
  };
  selecaoDRE = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("DRE - DIRETORIA REGIONAL DE EDUCACAO IPIRANGA");
  };
  selecaoDRETESTE = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("DRE - DIRETORIA REGIONAL DE EDUCACAO CAMPO LIMPO (TESTE)");
  };
  selecaoCEUEMEF = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU EMEF - MARIO FITTIPALDI");
  };
  selecaoCEUEMEFTESTE = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("CEU EMEF - MARIO FITTIPALDI (TESTE)");
  };
  selecaoEMEI = () => {
    return cy
      .get('[data-testid="select-unidade"]')
      .select("EMEI - MARIO SETTE");
  };

  //-----------Notificações, Perfil e Sair---------\\
  botaoPerfil = () => {
    return cy.get(".span-text-dropdown");
  };
  botaoMeusDados = () => {
    return cy.get(".btn-sair").contains("Meus dados");
  };
  botaoSair = () => {
    return cy.get(".btn-sair").contains("Sair");
  };
  botaoSairSistema = () => {
    return cy.get(".btn-success");
  };

  //-----------------------Menu de Navegação-------------------------\\

  menuParametrizacoes = () => {
    return cy.get('[data-cy="Parametrizações"]');
  };
  menuResumoDosRecursos = () => {
    return cy.get('[data-cy="Resumo dos recursos"]');
  };
  menuCreditosDaEscola = () => {
    return cy.get('[data-cy="Créditos da escola"]');
  };
  menuGastosDaEscola = () => {
    return cy.get('[data-cy="Gastos da escola"]');
  };
  menuPrestacaoContas = () => {
    return cy.get('[data-cy="Prestação de contas"]');
  };
  menuGeracaoDocumentos = () => {
    return cy.get("#geracao_documento");
  };
}

export default ComumElementosPTRF;
