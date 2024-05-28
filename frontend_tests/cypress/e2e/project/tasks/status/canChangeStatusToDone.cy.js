import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks[5];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('jean');
    cy.createProject('status done');
  });

  it('changes the status to done', () => {
    cy.visit(`/projects`);
    cy.contains('status done').first().click({ force: true });
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');
    cy.createTask(currentTask.fields.intent);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.contains(currentTask.fields.intent);
    cy.get('[data-test-id="done-status-task-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="send-status-3-feedback-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="done-status-task-button"]').should(
      'have.class',
      'bg-green-dark'
    );

    cy.contains(currentTask.fields.intent).click({ force: true });
    cy.contains(currentTask.fields.intent);

    const now = new Date();
    cy.contains(
      `a changé le statut de la recommandation en faite le ${now.toLocaleDateString()}`
    );
  });
});
