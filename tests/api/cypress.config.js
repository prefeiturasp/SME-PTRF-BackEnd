const { defineConfig } = require("cypress");
const allureWriter = require('@shelex/cypress-allure-plugin/writer');
require('dotenv').config()

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      allureWriter(on, config);
      require ('./cypress/plugin/index')(on, config)
      return config;
    },
    baseUrlPTRF: 'https://test-sig-escola.sme.prefeitura.sp.gov.br/login',
    baseUrlPTRFHomol: 'https://hom-sig-escola.sme.prefeitura.sp.gov.br/',
    usuario_homol_sme: process.env.USUARIO_HOMOL_SME,
    usuario_homol_dre: process.env.USUARIO_HOMOL_DRE,
    senha_homol: process.env.SENHA_HOMOL,
    viewportWidth: 1600,
    viewportHeight: 1050,
    video: false,
		timeout: 900000,
		videoCompression: 0,
		retries: 1,
		screenshotOnRunFailure: true,
		chromeWebSecurity: false,
		experimentalRunAllSpecs: true,
		failOnStatusCode: false,
		specPattern: 'cypress/e2e/**/**/*.{feature,cy.{js,jsx,ts,tsx}}',
  },
});

