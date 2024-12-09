const taskName = 'to inprogress';
let currentProjectId;

describe('I can go to tasks tab', () => {
  const TASK_STATUSES = [0, 1, 2, 3];

  beforeEach(() => {
    cy.visit('/');

    cy.login('conseiller1');
    cy.createProject('dragndroptest').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('drags n drops no status task to in progress status', () => {
    cy.visit(`/project/${currentProjectId}`);

    cy.becomeAdvisor(currentProjectId);
    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask(taskName);

    cy.get('[data-test-id="kanban-tasks-switch-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="kanban-tasks-switch-button"]').should('be.checked');

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

// page recommandation
