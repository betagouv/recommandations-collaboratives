// import resources from '../../../../fixtures/resources/resources.json'

// const currentResource = resources[4]
const taskName = 'task intent';
let currentProjectId;

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('new task').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('creates a task with a resource and see the initial comment', () => {
    cy.visit(`/project/${currentProjectId}`);
    cy.becomeAdvisor(currentProjectId);

    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask(taskName, '', true);
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.get('[data-test-id="task-initial-comment"]').should('exist');
  });
});
