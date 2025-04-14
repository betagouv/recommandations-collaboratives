describe('I can go to tasks tab @page-projet-recommandations', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/30/actions`);
  });

  it('change task position to top', () => {
    // Buttons up should not be visible on the first element
    cy.get('[data-test-id="task-item"]')
      .get('[data-cy="move-task-above"]')
      .should('not.be.visible');
    cy.get('[data-test-id="task-item"]')
      .get('[data-cy="move-task-to-top"]')
      .should('not.be.visible');
    // Buttons down should not be visible on the last element
    cy.get('[data-test-id="task-item"]')
      .last()
      .get('[data-cy="move-task-below"]')
      .should('not.be.visible');
    cy.get('[data-test-id="task-item"]')
      .get('[data-cy="move-task-to-bottom"]')
      .should('not.be.visible');
    // Move last task to the top
    cy.get('[data-test-id="task-item"]')
      .last()
      .should('contains.text', 'Task order 2');
    cy.get('[data-cy="move-task-to-top"]').last().click();
    cy.get('[data-test-id="task-item"]').should(
      'contains.text',
      'Task order 2'
    );
  });

  it('change task position bottom', () => {
    // Move last task to the bottom
    cy.get('[data-test-id="task-item"]').should(
      'contains.text',
      'Task order 2'
    );
    cy.get('[data-cy="move-task-to-bottom"]').first().click();
    cy.get('[data-test-id="task-item"]')
      .last()
      .should('contains.text', 'Task order 2');
  });

  it('change task position above', () => {
    // Move last task to the above
    cy.get('[data-test-id="task-item"]')
      .last()
      .should('contains.text', 'Task order 2');
    cy.get('[data-cy="move-task-above"]').last().click();
    cy.get('[data-test-id="task-item"]')
      .last()
      .should('contains.text', 'Task order 1');
  });

  it('change task position below', () => {
    // Move last task to the below
    cy.get('[data-cy="move-task-below"]').last().click();
    cy.get('[data-test-id="task-item"]')
      .last()
      .should('contains.text', 'Task order 2');
  });
});
