import projects from '../../../../fixtures/projects/projects.json';

const currentProject = projects[1]; // pk 2 - conseiller1 advisor
// pk 36 - conseiller1 advisor, published fixture reco "Reco à suivre fixture".
const advisorTestProject = projects.find((p) => p.pk === 36);

describe('I can search and share a contact on a message editor @page-projet-recommandations-modification', () => {
  it('can search, select and share a contact on a reply to a recommendation', () => {
    const now = new Date();
    cy.login('conseiller1');
    cy.visit(`/project/${advisorTestProject.pk}/conversations`);

    cy.get('[data-test-id="message-reply-button"]').first().click({
      force: true,
    });
    cy.shareContact('Lala');
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(
      `Voici mon contact ${now}`,
      { force: true }
    );
    cy.get('[data-test-id="send-message-conversation"]').click({
      force: true,
    });

    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it('can search, select and share a contact on a conversation', () => {
    cy.login('staff');
    cy.visit(`/project/${currentProject.pk}/conversations`);

    //fonction to search and attach a contact
    cy.shareContact('Lala');

    //write a message
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(
      'Here is my contact',
      { force: true }
    );

    //validate message on conversation
    cy.get('[data-test-id="send-message-conversation"]').click({ force: true });
    //my contact should be visible on the conversation
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it('can search, select and share a contact on advisor space', () => {
    cy.login('staff');
    cy.visit(`/project/${currentProject.pk}/suivi`);

    //fonction to search and attach a contact
    cy.shareContact('Lala');

    //write a message
    cy.get('[data-test-id="tiptap-editor-content"] .ProseMirror').type(
      'Here is my contact',
      { force: true }
    );

    //validate message on advisor space
    cy.get('[data-test-id="submit-message-button-on-advisor-space"]').click({
      force: true,
    });

    //my contact should be visible on the advisor space
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it.skip('can create a contact, an organization and a national group and share the contact on a new task', () => {});
});
