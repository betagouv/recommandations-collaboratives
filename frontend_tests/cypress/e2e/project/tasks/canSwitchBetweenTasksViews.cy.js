import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[1];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('switch between inline & kanban view', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor(currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du projet
    cy.visit(`/project/${currentProject.pk}/actions`);
    cy.createTask('test');

    cy.get('[data-test-id="kanban-tasks-switch-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="kanban-tasks-switch-button"]').should('be.checked');

    cy.get('[data-test-id="list-tasks-switch-button"]').click({ force: true });
    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
  });
});

// page recommandations
