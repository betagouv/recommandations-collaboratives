let currentProjectId;
describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('draft project').then((projectId) => {
      currentProjectId = projectId;
      cy.logout();
    });
  });

  it('publishes a task', () => {
    cy.login('conseiller2');
    cy.visit(`/project/${currentProjectId}/actions`).then(() => {
      cy.becomeAdvisor(currentProjectId);
      cy.visit(`/project/${currentProjectId}/actions`);

      cy.createTask('draft project');

      cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

      cy.get('#unpublish-task-button').click({ force: true });
      cy.get('[data-test-id="task-draft-status"]').should('be.visible');
      cy.get('#publish-task-button').click({ force: true });
      cy.get('[data-test-id="task-draft-status"]').should('not.exist');
    });
  });
});
