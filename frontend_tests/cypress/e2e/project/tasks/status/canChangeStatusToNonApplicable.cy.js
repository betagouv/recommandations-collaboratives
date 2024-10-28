import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks[6];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('status not');
  });

  it('changes the status to non applicable', () => {
    cy.visit('/projects');
    cy.contains('status not').click({ force: true });

    cy.becomeAdvisor();

    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask(currentTask.fields.intent);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.contains(currentTask.fields.intent);

    cy.get('[data-test-id="not-interested-status-task-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="send-status-4-feedback-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="not-interested-status-task-button"]').should(
      'have.class',
      'bg-grey-dark'
    );

    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    const now = new Date();
    cy.contains(
      `a changé le statut de la recommandation en non applicable le ${now.toLocaleDateString()}`
    );
  });
});
