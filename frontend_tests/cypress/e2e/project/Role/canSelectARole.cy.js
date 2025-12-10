import projectView from '../../../support/views/project';

describe('I can go to a project and select my role on it', () => {

  it('can become observer, advisor or quit project as regional advisor', () => {
    cy.login('jean');
    cy.visit('/project/2');

    cy.get('[data-test-id="select-observer-or-advisor-button"]').click({ force: true });
    cy.get('[data-test-id="button-quit-role"]').click({ force: true });
    cy.get('[data-test-id="select-observer-or-advisor-button"]').should('include.text', 'Rejoindre');

    cy.get('[data-test-id="select-observer-or-advisor-button"]').click({ force: true });
    cy.get('[data-test-id="button-become-advisor"]').click({ force: true });
    cy.get('[data-test-id="select-observer-or-advisor-button"]').should('include.text', 'Quitter');

  });
});
