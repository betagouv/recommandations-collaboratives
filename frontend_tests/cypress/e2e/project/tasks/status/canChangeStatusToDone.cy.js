import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks[5];
let currentProjectId;

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('status done').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('changes the status to done', () => {
    cy.visit(`/project/${currentProjectId}`);
    cy.becomeAdvisor(currentProjectId); // A remplacer par une fixture avec un user déjà advisor du projet
    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask(currentTask.fields.intent);
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
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

// page recommandation
