import projects from '../../../fixtures/projects/projects.json';

let currentProject = projects[9];

describe('I can go to overview tab and check invitation advisor button', () => {
  before(() => {
    cy.login('staff');
    cy.createProject('non advisor project');
    cy.visit('/projects/moderation');
    cy.get('[data-test-id="accept-project"]').first().click();
    cy.logout();
  });

  it('shows disabled button to invite new advisor', () => {
    cy.login('national');
    cy.visit('/projects/advisor/');
    cy.contains('non advisor project').click({ force: true });
    cy.url('should.include', '/presentation');
    cy.get('[data-cy="invite-advisor-button"]').should('be.disabled');
  });
});
