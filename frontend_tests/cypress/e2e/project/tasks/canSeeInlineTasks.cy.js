import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('jean');
  });

  it('list all inline tasks', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask(1);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
  });
});
