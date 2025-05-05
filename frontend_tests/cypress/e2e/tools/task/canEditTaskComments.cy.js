import projects from '../../../fixtures/projects/projects.json';

const currentProject = projects[2];
const message = 'Message - Test comment on task';

describe('As advisor, I can make a comment on a task', () => {
  it('adds a new comment, and stops from submitting the comment more than once', () => {
    cy.login('conseiller1');
    cy.visit(`/project/${currentProject.pk}/actions`);

    cy.get('[data-test-id="list-tasks-switch-button"]').should('be.checked');
    cy.get('[data-test-id="task-initial-comment"]').should('exist');

    cy.get('[data-test-id="edit-comment-button"]')
      .first()
      .click({ force: true });

    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').click();
    cy.focused().type(message, {
      force: true,
      delay: 0,
    });

    cy.get('[data-test-id="button-submit-new"]').click({ force: true });
    cy.get('[data-test-id="task-initial-comment"]').should('contain', message);
  });
});
