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

  it('posts a followup with today\'s date and see it', () => {
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.createTask(task3.fields.intent);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');

    cy.contains(task3.fields.intent).click({ force: true });

    const now = new Date();

    cy.get('.ProseMirror p').click();
    cy.focused().type(`test followup ${now}`, { force: true, delay: 0 });

    cy.get('[data-test-id="button-submit-new"]').click();
    cy.get('[data-cy="column-list-comment"]')
      .should('contain', `${currentUser.fields.first_name}`)
      .should('contain', `${currentUser.fields.last_name}`)
      .should('contain', `test followup ${now}`);
  });
});

// page recommandation
