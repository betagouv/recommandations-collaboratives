import projects from '../../../../fixtures/projects/projects.json';
import tasks from '../../../../fixtures/projects/tasks.json';

const currentProject = projects[1];
const task2 = tasks[1];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.becomeAdvisor(currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du dossier
  });

  it('opens a modal with the task', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.createTask(task2.fields.intent);
    cy.contains(task2.fields.intent).click({ force: true });
    cy.contains(task2.fields.intent);
  });
});

// page recommandation
