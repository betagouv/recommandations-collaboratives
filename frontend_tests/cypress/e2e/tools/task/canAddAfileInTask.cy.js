import file from '../../../fixtures/documents/file.json';

let currentProjectId;

describe('I can add a file in a task', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.createProject('file in task').then((projectId) => {
      currentProjectId = projectId;
    });
  });

  it('writes a message with a file', () => {
    cy.visit(`/project/${currentProjectId}`);

    cy.becomeAdvisor(currentProjectId);
    cy.visit(`/project/${currentProjectId}/actions`);

    cy.get("[data-test-id='submit-task-button']").click({ force: true });

    cy.get('#push-noresource').click({ force: true });

    const now = new Date();

    cy.get('#intent')
      .type('fake recommandation with no resource', { force: true })
      .should('have.value', 'fake recommandation with no resource');

      cy.get('.ProseMirror p').click();
      cy.focused().type(`fake recommandation content with no resource : ${now}`);

    cy.get('[name="the_file"]').selectFile(file.path, { force: true });

    cy.get('[type=submit]').click({ force: true });

    cy.url().should('include', '/actions');

    cy.contains(`fake recommandation content with no resource`);
  });
});
