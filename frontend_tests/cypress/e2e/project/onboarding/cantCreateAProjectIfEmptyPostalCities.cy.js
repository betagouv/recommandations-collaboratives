import project from '../../../fixtures/projects/project.json';
import communes from '../../../fixtures/geomatics/commune.json';

const projectCommune = communes.find(
  (c) => c.fields.postal == project.postcode
);

describe('I cant create a dossierc if the postal cities are empty', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the onboarding page and trigger an error if the postal is set but returns 0 cities', () => {
    cy.visit('/');

    cy.get('[data-test-id="button-need-help"]')
      .contains('Solliciter')
      .click({ force: true });

    cy.url().should('include', '/onboarding/project');

    cy.get('#id_name')
      .should('not.have.class', 'fr-input--error')
      .type(project.name)
      .should('have.value', project.name)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_location')
      .should('not.have.class', 'fr-input--error')
      .type(project.location)
      .should('have.value', project.location)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_description')
      .should('not.have.class', 'fr-input--error')
      .type(project.description)
      .should('have.value', project.description)
      .should('have.class', 'fr-input--valid');

    cy.get('button[type="submit"]').click();

    cy.url().should('include', '/onboarding/project');

    cy.get('[data-test-id="input-postcode"]')
      .parent()
      .should('have.class', 'fr-input-group--error');

    cy.get('[data-test-id="select-city"]')
      .parent()
      .should('have.class', 'fr-select-group--error');
  });
});
