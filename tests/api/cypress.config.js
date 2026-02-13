const { defineConfig } = require("cypress");
const allureWriter = require("@shelex/cypress-allure-plugin/writer");
const { cloudPlugin } = require("cypress-cloud/plugin");
require("dotenv").config();

module.exports = defineConfig({
  e2e: {
    supportFile: "cypress/support/e2e.js",

    async setupNodeEvents(on, config) {
      allureWriter(on, config);
      require("./cypress/plugin/index")(on, config);
      return cloudPlugin(on, config);
    },

    env: {
      TAGS: "not @ignore"
    },

    baseUrlPTRF: "https://qa-sig-escola.sme.prefeitura.sp.gov.br/login-suporte",
    baseUrlPTRFHomol: "https://qa-sig-escola.sme.prefeitura.sp.gov.br/",
    usuario_homol_sme: process.env.USUARIO_HOMOL_SME,
    usuario_homol_dre: process.env.USUARIO_HOMOL_DRE,
    usuario_homol_ue: process.env.USUARIO_HOMOL_UE,
    senha_homol: process.env.SENHA_HOMOL,
    senha_teste: process.env.SENHA_TESTE,
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
    specPattern: "cypress/e2e/**/**/*.{feature,cy.{js,jsx,ts,tsx}}",
  },
});