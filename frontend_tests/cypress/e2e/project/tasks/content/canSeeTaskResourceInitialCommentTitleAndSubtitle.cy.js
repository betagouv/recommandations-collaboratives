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
    cy.becomeAdvisor(currentProjectId); // A remplacer par une fixture avec un user déjà advisor du projet

    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask(taskName, '', true);
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.get('[data-test-id="task-initial-comment"]').should('exist');
    cy.contains(currentResource.fields.subtitle);
    cy.contains(currentResource.fields.title);
  });
});

// page recommandation
