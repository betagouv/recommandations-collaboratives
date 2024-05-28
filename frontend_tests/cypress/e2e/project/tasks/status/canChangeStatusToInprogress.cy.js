import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks[4];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.createProject('status inprogress');
  });

  it('changes the status to in progress', () => {
    cy.visit(`/projects`);
    cy.contains('status inprogress').first().click({ force: true });
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask(currentTask.fields.intent);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.contains(currentTask.fields.intent);

    cy.get('[data-test-id="in-progress-status-task-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="in-progress-status-task-button"]').should(
      'have.class',
      'bg-blue'
    );

    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    const now = new Date();
    cy.contains(
      `a changé le statut de la recommandation en en cours le ${now.toLocaleDateString()}`
    );
  });
});
