const { defineConfig } = require('cypress')

module.exports = defineConfig({
  chromeWebSecurity: false,
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config)
    },
    chromeWebSecurity: false,
    baseUrl: 'http://example.localhost:8000/',
    video:false,
    experimentalSessionAndOrigin:true
  },
  "hosts": {
    "*.localhost": "127.0.0.1"
  }
})
