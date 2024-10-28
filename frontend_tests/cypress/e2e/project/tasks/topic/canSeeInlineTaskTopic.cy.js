describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('test project');
  });

  it('sees a task inline topic', () => {
    cy.visit('/projects');
    cy.contains('test project').click({ force: true });
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask('inline task', 'inline topic');

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.get('[data-test-id="task-inline-topic"]').should('exist');
  });
});
