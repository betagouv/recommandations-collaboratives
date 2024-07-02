import project from '../../../fixtures/projects/project.json';

const projectName = 'New project onboarding answer';

describe('I can see onboarding answer on the overview tab', () => {
  before(() => {
    cy.login('bob');
    cy.createProject(projectName);
    cy.logout();
  });

  afterEach(() => {
    cy.logout();
  });

  it('should see the project description on overview tab as staff', () => {
    cy.login('staff');
    cy.visit('/projects');
    cy.contains(projectName).first().click({ force: true });
    cy.get('[data-test-id="project-information-card-context"]').should(
      'contain.text',
      project.description
    );
  });

  it('should see the project description on overview tab as collectivity', () => {
    cy.login('bob');
    cy.visit('/');
    cy.contains(projectName).parent().find('a').click({ force: true });
    cy.get('[data-test-id="project-information-card-context"]').should(
      'contain.text',
      project.description
    );
  });

  // TODO add fixture for complete questions onboarding
});
