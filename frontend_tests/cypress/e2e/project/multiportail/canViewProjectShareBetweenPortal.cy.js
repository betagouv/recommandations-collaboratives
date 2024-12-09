describe('Project share between portal', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('display share by and with portal on kanban', () => {
    cy.visit('/projects');
    cy.get('[data-cy="kanban-project-shared-by-origin"]')
      .should('be.visible')
      .should('include.text', 'example2');
    cy.get('[data-cy="kanban-project-shared-with"]')
      .should('be.visible')
      .should('include.text', 'example3');
  });

  it('display share by portal on moderation', () => {
    cy.visit('/projects/moderation');
    cy.get('[data-cy="moderation-projet-shared-by"]')
      .should('be.visible')
      .should('include.text', 'example2');
  });
});
