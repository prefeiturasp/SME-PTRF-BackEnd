import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Quando('clico na opção Créditos da escola', () => { 
  cy.clicar_creditos_da_escola() 
})

Entao('sistema exibe {string} nos créditos da UE', (campo) => {
  cy.validar_creditos_da_escola(campo)
})

Entao('valida os totais de créditos da UE', () => {
  cy.validar_somas_creditos_ue()
})

Quando('seleciono o filtro por tipo {string}', (campo) => {
  cy.selecionar_filtro_creditos_da_escola(campo)
})

Entao('sistema filtra por tipo {string} nos créditos da UE', (campo) => {
  cy.validar_filtro_selecionado_creditos_da_escola(campo)
})

Entao('sistema valida o total filtrado de repasse nos créditos da UE', () => {
  cy.validar_total_filtrado_repasse_creditos_ue()
})

Dado('aciono mais filtros em créditos da escola', () => {
  cy.acionar_mais_filtros_creditos_da_escola()
})

Dado('preencho o filtro detalhamento do crédito com {string}', (detalhamento) => {
  cy.preencher_filtro_detalhamento_credito(detalhamento)
})

Dado('preencho o filtro conta com {string}', () => {
  cy.preencher_filtro_conta_creditos_da_escola()
})

Dado('preencho o filtro ação com {string}', (acao) => {
  cy.preencher_filtro_acao_creditos_da_escola(acao)
})

Dado('preencho o filtro período de com {string}', (dataDe) => {
  cy.preencher_filtro_periodo_de_creditos_da_escola(dataDe)
})

Dado('preencho o filtro período até com {string}', (dataAte) => {
  cy.preencher_filtro_periodo_ate_creditos_da_escola(dataAte)
})

Dado('preencho os filtros de créditos da escola conforme o caso {string}', (caso) => {
  cy.preencher_filtros_creditos_da_escola_por_caso(caso)
})

Entao('sistema filtra por detalhamento do crédito {string} nos créditos da UE', (detalhamento) => {
  cy.validar_filtro_detalhamento_credito(detalhamento)
})

Entao('sistema filtra por conta {string} nos créditos da UE', () => {
  cy.validar_filtro_conta_creditos_da_escola()
})

Entao('sistema filtra por ação {string} nos créditos da UE', (acao) => {
  cy.validar_filtro_acao_creditos_da_escola(acao)
})

Entao('sistema filtra por período inicial {string} nos créditos da UE', (dataDe) => {
  cy.validar_filtro_periodo_de_creditos_da_escola(dataDe)
})

Entao('sistema filtra por período final {string} nos créditos da UE', (dataAte) => {
  cy.validar_filtro_periodo_ate_creditos_da_escola(dataAte)
})

Entao('sistema filtra os créditos da UE conforme {string}', (caso) => {
  cy.validar_filtros_creditos_da_escola_por_caso(caso)
})

Entao('sistema filtra os dados com todos os filtros nos créditos da UE', () => {
  cy.validar_todos_os_filtros_creditos_da_escola()
})

Entao('sistema valida o botão {string} nos créditos da UE', (botao) => {
  cy.validar_botoes_creditos_ue(botao)
})

Entao('abre a exibição no botão {string} nos créditos da UE', (botao) => {
  cy.validar_valores_reprogramados_ue(botao)
})

Dado('abro a tela de valores reprogramados nos créditos da UE', () => {
  cy.validar_valores_reprogramados_ue('valores reprogramados')
})

Entao('sistema valida a soma os valores reprogramados da UE', (tipoConta) => {
  cy.validar_soma_valores_reprogramados_ue(tipoConta)
})

Dado('cadastro {string} como crédito da escola', (campo) => {
  cy.cadastrar_creditos_da_escola_ue(campo)
})

Entao('sistema insere {string} nos créditos da UE', () => {
})

Dado('cadastro crédito da escola sem preencher os dados', () => {
  cy.clicar_creditos_da_escola()
})

Entao('sistema não permite salvar créditos da UE', () => {
  cy.validar_campos_cadastrar_creditos_da_escola_ue()
<<<<<<< HEAD
})

Dado('cadastro a {string} como crédito da escola', () => {
  cy.cadastrar_devolucao_creditos_da_escola_ue()
})

Entao('sistema insere a {string} nos créditos da UE', () => {
=======
>>>>>>> 0faf44dfc85aaa809de68c17c46ea139175091d3
})