let currentProjectId;

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('test project 2').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('sees a task kanban topic', () => {
    cy.visit(`/project/${currentProjectId}`);
    cy.becomeAdvisor(currentProjectId); // A remplacer par une fixture avec un user déjà advisor du projet
    cy.visit(`/project/${currentProjectId}/actions`);

    cy.createTask('inline task', 'kanban topic');

    cy.get('[data-test-id="kanban-tasks-switch-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="kanban-tasks-switch-button"]').should('be.checked');
    cy.get('[data-test-id="task-kanban-topic"]').should('exist');
    cy.get('[data-test-id="list-tasks-switch-button"]').click({ force: true });
    cy.get('[data-test-id="task-inline-topic"]').should('exist');
  });
});

// page recommandation
