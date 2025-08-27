describe('I can search and share a contact on a message editor', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('can search, select and share a contact on a followup', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });

    //fonction to search and attach a contact
    cy.shareContact('Lala');

    //validate message followup
    cy.get('[data-test-id="button-submit-new"]').click({ force: true });
    //my contact should be visible on the followup
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it('can search, select and share a contact on a conversation', () => {
    cy.visit(`/project/2/conversations`);

    //fonction to search and attach a contact
    cy.shareContact('Lala');

    //write a message
    cy.get('[data-test-id="tiptap-editor-content"]').type('Here is my contact');

    //validate message on conversation
    cy.get('[data-test-id="send-message-conversation"]').click({ force: true });
    //my contact should be visible on the conversation
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it('can search, select and share a contact on advisor space', () => {
    cy.visit(`/project/2/suivi`);

    //fonction to search and attach a contact
    cy.shareContact('Lala');

    //write a message
    cy.get('[data-test-id="tiptap-editor-content"]').type('Here is my contact');

    //validate message on advisor space
    cy.get('[data-test-id="submit-message-button-on-advisor-space"]').click({
      force: true,
    });

    //my contact should be visible on the advisor space
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  it('can create a contact, an organization and a national group and share the contact on a new task', () => {
    cy.visit(`/project/2/actions#`);
    //click on create recommandation
    cy.get('[data-test-id="create-task-button"]').click({ force: true });

    //create a recommandation without resource
    cy.get('[data-cy="radio-push-reco-no-resource"]').click({
      force: true,
    });
    //write resource title
    cy.get('[data-cy="input-title-task"]').type('Test contact');
    //write a message
    cy.get('[data-test-id="tiptap-editor-content"]').type('Here is my contact');
    //click on add contact button
    cy.get('[data-test-id="button-add-contact-in-editor"]').click({
      force: true,
    });
    //create a contact
    cy.get('[data-test-id="button-create-contact"]').click({
      force: true,
    });
    //search an non existing organization
    cy.get('#search-organization-input').type('Test organization');
    //create an organization
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    cy.get('#natGroup-yes').click({
      force: true,
    });
    cy.get('[data-test-id="search-group-input"]').type('Test group');
    //create a national group
    cy.get('[data-test-id="button-create-organization-group"]').click({
      force: true,
    });
    // create organization
    cy.get('[data-test-id="button-create-new-organization"]').click({
      force: true,
    });
    //create contact
    cy.get('[data-test-id="last-name"]').type('Test');
    cy.get('[data-test-id="first-name"]').type('Contact');
    cy.get('[data-test-id="job"]').type('testeur');
    cy.get('[data-test-id="email"]').type('test@test.test');
    cy.get('[data-test-id="phone"]').type('0123456789');
    cy.get('[data-test-id="create-contact-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    //save resource as draft
    cy.get('[data-test-id="publish-draft-task-button"]').click({
      force: true,
    });

    //my contact should be visible on the followup
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });
});
