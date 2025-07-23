describe('I can search or create and share a contact on a message editor', () => {
  beforeEach(() => {
    cy.login('jean');
  });

  xit('can search, select and share a contact on a followup', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //search for a contact
    cy.get('#search-contact-input')
      .type('Test', { force: true })
    //select a contact
    cy.get('[data-test-id="contact-to-select"]').first().click({ force: true });
    //send contact to tiptap editor
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({ force: true });
    //validate message followup
    cy.get('[data-test-id="button-submit-new"]').click({ force: true });
    //my contact should be visible on the followup
    cy.get('[data-test-id="contact-card"]').should('be.visible');
});

  xit('can create a contact and search an existing organization', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //create a new contact
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('#contact-first-name').type('New');
    cy.get('#contact-last-name').type('Contact');
    cy.get('#contact-email').type('new.contact@example.com');
    //search for an existing organization
    cy.get('#contact-organization').type('Existing Organization');
    //select the organization from the dropdown
    cy.get('[data-test-id="organization-select"]').find('li').contains('Existing Organization').click();
    //submit the contact form
    cy.get('[data-test-id="button-submit-new-contact"]').click({ force: true });
    //verify that the contact is created and organization is linked
    cy.get('[data-test-id="contact-card"]').should('contain', 'New Contact')
      .and('contain', 'Existing Organization');
  });

  xit('can create a contact and create a new organization with no group and no departments', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //create a new contact
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('#contact-first-name').type('New');
    cy.get('#contact-last-name').type('Contact');
    cy.get('#contact-email').type('new.contact@example.com');
    //create a new organization
    cy.get('#contact-organization').type('New Organization');
    //submit the contact form
    cy.get('[data-test-id="button-submit-new-contact"]').click({ force: true });
    //verify that the contact is created and organization is linked
    cy.get('[data-test-id="contact-card"]').should('contain', 'New Contact')
      .and('contain', 'New Organization');
  });

  xit('can create a contact and create a new organization with a group and no departments', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //create a new contact
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('#contact-first-name').type('New');
    cy.get('#contact-last-name').type('Contact');
    cy.get('#contact-email').type('new.contact@example.com');
    //create a new organization
    cy.get('#contact-organization').type('New Organization');
    //submit the contact form
    cy.get('[data-test-id="button-submit-new-contact"]').click({ force: true });
    //verify that the contact is created and organization is linked
    cy.get('[data-test-id="contact-card"]').should('contain', 'New Contact')
      .and('contain', 'New Organization');
    //create a new group
    cy.get('[data-test-id="button-create-group"]').click({ force: true });
    cy.get('#group-name').type('New Group');
    cy.get('[data-test-id="button-submit-new-group"]').click({ force: true });
    //verify that the group is created and linked to the organization
    cy.get('[data-test-id="group-card"]').should('contain', 'New Group')
      .and('contain', 'New Organization');
  });

  xit('can create a contact and create a new organization with a group and departments', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //create a new contact
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('#contact-first-name').type('New');
    cy.get('#contact-last-name').type('Contact');
    cy.get('#contact-email').type('new.contact@example.com');
    //create a new organization
    cy.get('#contact-organization').type('New Organization');
    //submit the contact form
    cy.get('[data-test-id="button-submit-new-contact"]').click({ force: true });
    //verify that the contact is created and organization is linked
    cy.get('[data-test-id="contact-card"]').should('contain', 'New Contact')
      .and('contain', 'New Organization');
    //create a new group
    cy.get('[data-test-id="button-create-group"]').click({ force: true });
    cy.get('#group-name').type('New Group');
    cy.get('[data-test-id="button-submit-new-group"]').click({ force: true });
    //verify that the group is created and linked to the organization
    cy.get('[data-test-id="group-card"]').should('contain', 'New Group')
      .and('contain', 'New Organization');
  });

});
