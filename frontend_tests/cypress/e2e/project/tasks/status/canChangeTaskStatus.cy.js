import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks.find((task) => task.pk === 53);

describe('I can go to tasks tab and change task status', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/27/actions`);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
    cy.contains(currentTask.fields.intent);
  });

  it('changes the status to done', () => {
    /**
     * Switch to "done" status
     */
    cy.get('[data-test-id="done-status-task-button"]').click({ force: true });
    cy.get('[data-test-id="done-status-task-button"]').should(
      'have.class',
      'bg-green-dark'
    );
    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    cy.contains(
      `a changé le statut de la recommandation en faite le ${new Date().toLocaleDateString()}`
    );
    cy.get('[data-test-id="close-modal-task"]').click();
  });
  it('changes the status to in progress', () => {
    cy.get('[data-test-id="in-progress-status-task-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="in-progress-status-task-button"]').should(
      'have.class',
      'bg-blue'
    );

    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    cy.contains(
      `a changé le statut de la recommandation en en cours le ${new Date().toLocaleDateString()}`
    );
  });
  it('changes the status to not interrested', () => {
    cy.get('[data-test-id="not-interested-status-task-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="not-interested-status-task-button"]').should(
      'have.class',
      'bg-grey-dark'
    );

    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    cy.contains(
      `a changé le statut de la recommandation en non applicable le ${new Date().toLocaleDateString()}`
    );
  });
});

// page recommandation
