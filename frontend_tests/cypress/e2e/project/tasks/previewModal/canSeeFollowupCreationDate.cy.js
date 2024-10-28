import projects from '../../../../fixtures/projects/projects.json';
import tasks from '../../../../fixtures/projects/tasks.json';

const currentProject = projects[1];
const task1 = tasks[0];

describe('I can go tasks tab', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('see creation date of a followup', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask(task1.fields.intent);
    cy.contains(task1.fields.intent).click({ force: true });
    cy.contains(task1.fields.intent);

    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );

    const now = new Date();

    cy.get('.ProseMirror p').then(($el) => {
      const el = $el.get(0); //native DOM element
      el.innerHTML = `test ${now}`;
    });

    cy.contains('Envoyer').click({ force: true });
    cy.contains(now.toLocaleDateString());
  });
});
