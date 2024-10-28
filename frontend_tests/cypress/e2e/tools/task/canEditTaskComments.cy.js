import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';
import editor from '../../../support/tools/editor';

const currentProject = projects[2];
const message = 'Message - Test comment on task';
const taskName = 'task intent';

describe('As advisor, I can make a comment on a task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('adds a new comment, and stops from submitting the comment more than once', () => {
    cy.visit(`/project/${currentProject.pk}`);
    cy.becomeAdvisor();
    cy.contains('Recommandations').click({ force: true });
    cy.url().should('include', '/actions');

    cy.createTask(taskName, '', true);
    // cy.createTask(taskName, '', true);
    cy.get('[data-test-id="list-tasks-switch-button"]').should(
      'have.class',
      'active'
    );
    cy.get('[data-test-id="task-initial-comment"]').should('exist');

    cy.get('[data-test-id="edit-comment-button"]')
      .first()
      .click({ force: true });
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(
      message,
      { force: true }
    );
    cy.get('[data-test-id="button-submit-edit"]').click({ force: true });
    cy.get('[data-test-id="task-initial-comment"]').should('contain', message);
  });
});
