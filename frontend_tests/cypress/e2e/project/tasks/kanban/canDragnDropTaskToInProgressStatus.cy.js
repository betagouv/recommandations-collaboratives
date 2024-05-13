const taskName = 'to inprogress';

describe('I can go to tasks tab', () => {
  const TASK_STATUSES = [0, 1, 2, 3];

  beforeEach(() => {
    cy.visit('/');

    cy.login('jean');
    cy.createProject('dragndroptest');
  });

  it('drags n drops no status task to in progress status', () => {
    cy.visit(`/projects`);
    cy.contains('dragndroptest').first().click({ force: true });

    cy.becomeAdvisor();

    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask(taskName);

    cy.get('[data-test-id="kanban-tasks-switch-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="kanban-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    // let droppableCoords = {}

    const fromStatus = TASK_STATUSES[0];
    const toStatus = TASK_STATUSES[1];
    const dataTransfer = new DataTransfer();

    const fromDataTest = `[data-test-id="board-targetable-${fromStatus}"]`;
    const toDataTest = `[data-test-id="board-targetable-${toStatus}"]`;
    cy.get(fromDataTest).trigger('dragstart', { dataTransfer });
    cy.get(toDataTest).trigger('drop', { dataTransfer });

    // TODO : finish this test to trigger api calls
  });
});
