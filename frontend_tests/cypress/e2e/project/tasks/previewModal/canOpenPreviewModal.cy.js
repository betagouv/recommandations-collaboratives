import projects from '../../../../fixtures/projects/projects.json';
import tasks from '../../../../fixtures/projects/tasks.json';

const currentProject = projects[1];
const task2 = tasks[1];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    cy.createTask(task2.fields.intent);
    cy.contains(task2.fields.intent).click({ force: true });
    cy.contains(task2.fields.intent);
  });
});
