describe('I can suppress a contact from the contactbook', () => {
    beforeEach(() => {

    });

    it('can suppress a contact from the contactbook as staff', () => {
        cy.login('staff');
        cy.visit(`/addressbook/contacts/`);
        cy.contains('[data-test-id="contact-card"]', 'à supprimer')
        .as('card');

        cy.get('@card').find('[data-test-id="button-delete-contact"]').click({ force: true });
        cy.get('@card').find('.modal__footer-confirm').click({ force: true });

        cy.contains('[data-test-id="contact-card"]', 'à supprimer').should('not.exist');
      });
});
