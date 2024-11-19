let currentProjectId;
describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('unpublish task').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('unpublishes a task', () => {
    cy.visit(`/projects`);
    cy.contains('unpublish task').first().click({ force: true });
    cy.becomeAdvisor(currentProjectId);

    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask('unpublish task');

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.get('#unpublish-task-button').click({ force: true });

    cy.contains('brouillon');
  });
});
