import projects from '../../../fixtures/projects/projects.json';

// pk 35 - conseiller1 advisor, published fixture reco "Reco à commenter fixture".
const currentProject = projects.find((p) => p.pk === 35);

describe('As advisor, I can reply to a recommendation in the conversation @page-projet-recommandations-modification', () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('replies to a recommendation message and sees the reply in the feed', () => {
    const now = new Date();
    const comment = `Message - Test comment on task ${now}`;

    cy.visit(`/project/${currentProject.pk}/conversations`);

    // Reply to the fixture recommendation message (the migrated equivalent of
    // a task followup).
    cy.get('[data-test-id="message-reply-button"]').first().click({
      force: true,
    });
    cy.contains('Vous êtes en train de répondre à un message');

    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror')
      .click()
      .type(comment, { delay: 0 })
      .should('contain.text', comment);
    cy.get('[data-test-id="send-message-conversation"]')
      .should('be.enabled')
      .click();

    cy.contains(comment);
  });
});
