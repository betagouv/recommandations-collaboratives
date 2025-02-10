describe('I can search and share a contact on a message editor', () => {
  beforeEach(() => {
    cy.login('jean');
  });

  it('can search, select and shar a contact on a foolowup', () => {
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

});
