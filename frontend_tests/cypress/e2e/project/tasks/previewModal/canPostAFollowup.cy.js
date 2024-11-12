import projects from '../../../../fixtures/projects/projects.json';
import tasks from '../../../../fixtures/projects/tasks.json';
import users from '../../../../fixtures/users/users.json';

const currentProject = projects[1];
const task3 = tasks[2];
const currentUser = users[1];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('posts a followup', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.createTask(task3.fields.intent);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.contains(task3.fields.intent).click({ force: true });

    const now = new Date();

    cy.get('.ProseMirror p').then(($el) => {
      const el = $el.get(0); //native DOM element
      el.innerHTML = `test ${now}`;
    });

    cy.contains('Envoyer').click({ force: true });
    cy.contains(`${currentUser.fields.first_name}`);
    cy.contains(`${currentUser.fields.last_name}`);

    cy.contains(`test ${now}`);
  });
});
