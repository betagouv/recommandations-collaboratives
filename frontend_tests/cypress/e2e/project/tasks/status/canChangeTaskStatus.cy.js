import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks.find((task) => task.pk === 53);

describe('I can go to tasks tab and change task status @page-projet-recommandations @page-projet-recommandations-status', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.visit(`/project/27/actions`);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
    cy.contains(currentTask.fields.intent);
  });

  it.skip('changes the status to done and verifies UI updates', () => {
    // Initial state check
    cy.get('[data-test-id="done-status-task-button"]').should(
      'not.have.class',
      'bg-green-dark'
    );

    // Change status to done
    cy.get('[data-test-id="done-status-task-button"]').click({ force: true });

    // Verify UI updates
    cy.get('[data-test-id="done-status-task-button"]')
      .should('have.class', 'bg-green-dark')
      .should('have.class', 'text-white')
      .should('have.class', 'border-green-dark')
      .should('have.class', 'pointer-events-none');

    // Verify other buttons are not active
    cy.get('[data-test-id="in-progress-status-task-button"]').should(
      'not.have.class',
      'bg-blue'
    );
    cy.get('[data-test-id="not-interested-status-task-button"]').should(
      'not.have.class',
      'bg-grey-dark'
    );

    // Verify status change in modal
    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(
      `a changé le statut de la recommandation en faite le ${new Date().toLocaleDateString()}`
    );
    cy.get('[data-test-id="close-modal-task"]').click();
  });

  it.skip('changes the status to in progress and verifies UI updates', () => {
    // Initial state check
    cy.get('[data-test-id="in-progress-status-task-button"]').should(
      'not.have.class',
      'bg-blue'
    );

    // Change status to in progress
    cy.get('[data-test-id="in-progress-status-task-button"]').click({
      force: true,
    });

    // Verify UI updates
    cy.get('[data-test-id="in-progress-status-task-button"]')
      .should('have.class', 'bg-blue')
      .should('have.class', 'text-white')
      .should('have.class', 'border-blue')
      .should('have.class', 'pointer-events-none');

    // Verify other buttons are not active
    cy.get('[data-test-id="done-status-task-button"]').should(
      'not.have.class',
      'bg-green-dark'
    );
    cy.get('[data-test-id="not-interested-status-task-button"]').should(
      'not.have.class',
      'bg-grey-dark'
    );

    // Verify status change in modal
    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(
      `a changé le statut de la recommandation en en cours le ${new Date().toLocaleDateString()}`
    );
  });

  it.skip('changes the status to not interested and verifies UI updates', () => {
    // Initial state check
    cy.get('[data-test-id="not-interested-status-task-button"]').should(
      'not.have.class',
      'bg-grey-dark'
    );

    // Change status to not interested
    cy.get('[data-test-id="not-interested-status-task-button"]').click({
      force: true,
    });

    // Verify UI updates
    cy.get('[data-test-id="not-interested-status-task-button"]')
      .should('have.class', 'bg-grey-dark')
      .should('have.class', 'text-white')
      .should('have.class', 'border-grey-dark')
      .should('have.class', 'pointer-events-none');

    // Verify other buttons are not active
    cy.get('[data-test-id="in-progress-status-task-button"]').should(
      'not.have.class',
      'bg-blue'
    );
    cy.get('[data-test-id="done-status-task-button"]').should(
      'not.have.class',
      'bg-green-dark'
    );

    // Verify status change in modal
    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(
      `a changé le statut de la recommandation en non applicable le ${new Date().toLocaleDateString()}`
    );
  });

  it('verifies status changes in modal view', () => {
    // Open the task modal
    cy.contains(currentTask.fields.intent).click({ force: true });

    // Change status to in progress in modal
    cy.get('#task-modal [data-test-id="in-progress-status-task-button"]').click(
      {
        force: true,
      }
    );

    // Verify status change in modal
    cy.get('#task-modal [data-test-id="in-progress-status-task-button"]')
      .should('have.class', 'bg-blue')
      .should('have.class', 'text-white')
      .should('have.class', 'border-blue');

    // Verify status change message appears
    cy.contains(
      `a changé le statut de la recommandation en en cours le ${new Date().toLocaleDateString()}`
    );

    // Change status to done in modal
    cy.get('#task-modal [data-test-id="done-status-task-button"]').click({
      force: true,
    });

    // Verify new status in modal
    cy.get('#task-modal [data-test-id="done-status-task-button"]')
      .should('have.class', 'bg-green-dark')
      .should('have.class', 'text-white')
      .should('have.class', 'border-green-dark');

    // Verify previous status button is no longer active
    cy.get(
      '#task-modal [data-test-id="in-progress-status-task-button"]'
    ).should('not.have.class', 'bg-blue');

    // Verify status change message appears
    cy.contains(
      `a changé le statut de la recommandation en faite le ${new Date().toLocaleDateString()}`
    );

    // Close modal and verify status persists
    cy.get('#task-modal [data-test-id="close-modal-task"]').click();
    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.get('#task-modal [data-test-id="done-status-task-button"]').should(
      'have.class',
      'bg-green-dark'
    );
  });
});

// page recommandation
