import projects from '../../../fixtures/projects/projects.json';

// pk 38 - conseiller1 advisor, dedicated to recommendation edition. The
const currentProject = projects.find((p) => p.pk === 38);

const intent = 'Reco dont on modifie le contenu';
const initialContent = 'Contenu initial de la recommandation';
const updatedContent = 'Contenu modifié depuis la conversation';

describe('As advisor, I can edit the content of a recommendation @page-projet-recommandations-modification', () => {
  beforeEach(() => {
    cy.login('conseiller1');
    cy.resetProjectRecommendations(currentProject.pk);
    cy.createTaskViaApi(currentProject.pk, {
      intent,
      content: initialContent,
      draft: false,
    });
  });

  it('edits a published recommendation from the conversation feed', () => {
    cy.visit(`/project/${currentProject.pk}/conversations`);

    cy.contains(initialContent);

    // Edit message with reco
    cy.get('[data-test-id="message-edit-recommendation"]')
      .first()
      .click({ force: true });
    cy.url().should('include', '/update/');

    cy.get('[data-cy="input-title-task"]').should('have.value', intent);
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').should(
      'contain.text',
      initialContent
    );

    // Replace the content and submit.
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror')
      .click()
      .type(`{selectall}{del}${updatedContent}`, { force: true, delay: 0 });
    cy.get('[data-cy="button-submit-task"]')
      .should('be.enabled')
      .click({ force: true });

    cy.url().should('include', `/project/${currentProject.pk}/conversations`);
    cy.contains(updatedContent);
    cy.contains(initialContent).should('not.exist');
  });
});
