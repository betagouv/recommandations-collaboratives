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

      cy.get('[data-test-id="submit-task-button"]').click();
      cy.get('[data-cy="reco-pusher-selected-project"]').should(
        'contains.text',
        'draft project'
      );
      cy.get('#push-noresource').click({ force: true });

      cy.get('#intent')
        .type(`draft project`, { force: true, delay: 0 })
        .should('have.value', `draft project`);

      cy.get('textarea')
        .type(`reco test from action description`, { force: true, delay: 0 })
        .should('have.value', `reco test from action description`);

      cy.get('.ProseMirror p').click();
      cy.focused().type('reco test for draft task');

      cy.get('[data-test-id="publish-draft-task-button"]').click();

      cy.url().should('include', '/actions');

      cy.contains('draft project');

      cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

      cy.get('#unpublish-task-button').click({ force: true });
      cy.get('[data-test-id="task-draft-status"]').should('be.visible');
      cy.get('#publish-task-button').click({ force: true });
      cy.get('[data-test-id="task-draft-status"]').should('not.exist');
      cy.get('[data-test-id="update-task-action-button"]').click({
        force: true,
      });
      cy.get('textarea').type(
        `reco test from action description modification`,
        { force: true, delay: 0 }
      );
      cy.get('[data-cy="button-submit-task"]').click();
      cy.url().should('include', '/actions');
      cy.contains('reco test from action description modification');
    });
  });
});

// page recommandations
