describe('I can search and share a contact on a message editor', () => {
  beforeEach(() => {
    cy.login('jean');
  });

  it('can search, select and shar a contact on a foolowup', () => {
    cy.visit(`/project/2/action`);

    cy.get('[data-test-id="task-item"]').click({ force: true });
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });

    cy.get('#search-contact-input')
      .type('Test', { force: true })

    cy.get('[data-test-id="contact-to-select"]').click({ force: true });
    cy.get('[data-test-id="button-submit-new"]').click({ force: true });

    cy.get('[data-test-id="contact-to-select"]').should('be.visible');
});

});
