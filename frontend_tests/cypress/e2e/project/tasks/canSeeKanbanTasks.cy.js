import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('list all kanban tasks', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask('test');

    cy.get('[data-test-id="kanban-tasks-switch-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="kanban-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
  });
});
