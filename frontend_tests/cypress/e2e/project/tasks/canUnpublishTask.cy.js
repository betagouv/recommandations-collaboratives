describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('unpublish task');
  });

  it('unpublishes a task', () => {
    cy.visit(`/projects`);
    cy.contains('unpublish task').first().click({ force: true });
    cy.becomeAdvisor();

    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask('unpublish task');

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    cy.get('#unpublish-task-button').click({ force: true });

    cy.contains('brouillon');
  });
});
