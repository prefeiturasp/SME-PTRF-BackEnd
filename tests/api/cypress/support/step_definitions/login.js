import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

const Dado = Given
const Quando = When
const Entao = Then

Dado('eu acesso o sistema com a visualização {string}', function (visualizacao) {
	cy.configurar_visualizacao(visualizacao)
});

Dado('realizo login no sistema PTRF com perfil {string}', function (perfil) {
cy.realizar_login(perfil)
  });