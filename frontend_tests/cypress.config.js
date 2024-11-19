const { defineConfig } = require('cypress');

module.exports = defineConfig({
  viewportWidth: 1920,
  viewportHeight: 1080,
  reporter: 'cypress-mochawesome-reporter',
  reporterOptions: {
    charts: true,
    reportPageTitle: 'Recoco FE tests',
    embeddedScreenshots: true,
    inlineAssets: true,
    saveAllAttempts: false,
    videoOnFailOnly: true,
    screenshotOnRunFailure: false,
  },
  chromeWebSecurity: false,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      require('cypress-mochawesome-reporter/plugin')(on);
      require('./cypress/plugins/index.js')(on, config);
      require('@cypress/grep/src/plugin')(config);
      return config;
    },
    chromeWebSecurity: false,
    // baseUrl: 'http://example.localhost:8000/',
    video: false,
  },
  hosts: {
    '*.localhost': '127.0.0.1',
  },
});
