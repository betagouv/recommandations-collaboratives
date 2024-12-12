import editor from '../../../support/tools/editor';
import file from '../../../fixtures/documents/file.json';
const currentProjectId = 25;

describe('I can access tabs and see notifications', () => {
  before(() => {
    cy.login('collectivité1');
    cy.visit(`/project/${currentProjectId}/presentation`);
    cy.get('[data-test-id="badge-tab-new-task"]').should('not.exist');
    cy.get('[data-test-id="badge-tab-new-message"]').should('not.exist');
    cy.get('[data-test-id="badge-tab-new-file"]').should('not.exist');
    cy.logout();

    cy.login('conseiller1');
    // Create a task to have a notification
    cy.visit(`/project/${currentProjectId}/actions`);
    cy.createTask('Tâche notification');

    // Create message to have a notification
    cy.visit(`/project/${currentProjectId}/conversations`);
    const now = new Date();

    cy.get('textarea')
      .type(`test : ${now}`, { force: true })
      .should('have.value', `test : ${now}`);

    editor.writeMessage(`test : ${now}`);
    cy.contains('Envoyer').click({ force: true });
    cy.contains(`test : ${now}`);

    // Post a file to have a notification
    cy.visit(`/project/${currentProjectId}/documents`);

    cy.document().then((doc) => {
      var popover = doc.getElementById('popover');
      popover.style = 'display:block !important;';

      cy.get('[name="the_file"]').selectFile(file.path, { force: true });
      cy.get('#document-description')
        .type(file.description, { force: true, delay: 0 })
        .should('have.value', file.description);
      cy.get('#document-submit-button').click({ force: true });
    });

    cy.contains('Le document a bien été enregistré');
    cy.logout();
  });

  it('goes to the action page of my project', () => {
    cy.login('collectivité1');
    cy.visit(`/project/25/presentation`);
    cy.get('[data-test-id="badge-tab-new-task"]').should('exist');
    cy.get('[data-test-id="badge-tab-new-message"]').should('exist');
    cy.get('[data-test-id="badge-tab-new-file"]').should('exist');
  });
});
