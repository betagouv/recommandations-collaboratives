import projects from '../../../../fixtures/projects/projects.json';
import tasks from '../../../../fixtures/projects/tasks.json';

const currentProject = projects[1];
const task2 = tasks[1];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('staff');
    cy.becomeAdvisor(currentProject.pk);
  });

  it('opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.createTask(task2.fields.intent);
    cy.contains(task2.fields.intent).click({ force: true });
    cy.contains(task2.fields.intent);
  });
});
