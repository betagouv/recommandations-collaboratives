import projects from '../../../fixtures/projects/projects.json';
const currentProject = projects[1];

describe('I can go to tasks tab', () => {
  beforeEach(() => {
    cy.login('jean');
    // cy.createProject('delete task');
  });

  it('deletes a task', () => {
    cy.becomeAdvisor();
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask('test');

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    cy.get('[data-test-id="open-task-actions-button"]').then((el) => {
      const count3 = el.length;
      cy.wrap(count3).as('count');
    });

    cy.get('[data-test-id="open-task-actions-button"]').first().click({
      force: true,
    });
    cy.get('[data-test-id="delete-task-action-button"]').first().click({
      force: true,
    });
    cy.get('[data-test-id="delete-task-modal-button"]').click({
      force: true,
    });

    cy.get('@count').then((count) => {
      cy.get('[data-test-id="open-task-actions-button"]').should(
        'have.lengthOf',
        count - 1
      );
    });

    // the first test try to see if there are no tasks
    // Now we test if the list have one element less
    // cy.get('[data-test-id="no-tasks-banner"]').should('exist');
  });
});
