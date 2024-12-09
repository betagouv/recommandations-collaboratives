import tasks from '../../../../fixtures/projects/tasks.json';
const currentTask = tasks[4];
let currentProjectId;

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('status inprogress').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('changes the status to in progress', () => {
    cy.visit(`/project/${currentProjectId}`);
    cy.becomeAdvisor(currentProjectId);
    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask(currentTask.fields.intent);
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
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

// page recommandation
