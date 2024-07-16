import projects from '../../../fixtures/projects/projects.json';

let currentProject = projects[9];

describe('I can go to overview tab and check invitation advisor button', () => {
  before(() => {
    cy.login('staff');
    cy.createProject('non advisor project');
    cy.visit('/projects');
    cy.get('[data-cy="btn-accept-project"]').first().click();
    cy.logout();
    cy.login('national');
    cy.hideCookieBannerAndDjango();
  });

  it('shows disabled button to invite new advisor', () => {
    cy.visit('/projects/advisor/');
    cy.contains('non advisor project').click({ force: true });
    cy.url('should.include', '/presentation');
    cy.get('[data-cy="invite-advisor-button"]').should('be.disabled');
  });
});
