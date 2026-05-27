// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************
import 'cypress-mochawesome-reporter/register';

const url = require('url');

// reset baseUrl
Cypress.config('baseUrl', 'http://example.localhost:8001/');

// Import commands.js using ES2015 syntax:
import './commands';

// Alternatively you can use CommonJS syntax:
// require('./commands')

Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  return false;
});

// Neutralise le bandeau de consentement (composant Consent.js : le banner est masqué
// dès qu'un cookie dont le nom contient "cookie_consent" est présent). Sans ce
// pré-set, le bandeau couvre les inputs et fait échouer cy.type().
beforeEach(() => {
  cy.setCookie('cookie_consent', 'accepted', { domain: 'example.localhost' });
});

const registerCypressGrep = require('@cypress/grep');
registerCypressGrep();
