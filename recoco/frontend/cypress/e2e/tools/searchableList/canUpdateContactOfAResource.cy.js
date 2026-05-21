import contacts from '../../../fixtures/addressbook/contacts.json';

describe('I can assign new contacts when I edit a resource @acces-ressources', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to edit a resource suppress and assign 3 new contacts', () => {
    cy.visit('/ressource/1/');
    cy.get('[data-test-id="edit-resource"]').click();

    cy.get('[data-test-id="button-delete-contact"]').each(($el) => {
      cy.wrap($el).click({ force: true });
    });

    cy.get('#search-contact-input')
      .type('lala', { force: true })
      .should('have.value', 'lala');
    cy.get('[data-test-id="contact-card-component"]')
      .first()
      .click({ force: true });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    cy.get('#search-contact-input')
      .type('lili', { force: true })
      .should('have.value', 'lili');
    cy.get('[data-test-id="contact-card-component"]')
      .contains('lili')
      .click({ force: true });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    cy.get('#search-contact-input')
      .type('lulu', { force: true })
      .should('have.value', 'lulu');
    cy.get('[data-test-id="contact-card-component"]')
      .contains('lulu')
      .click({ force: true });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    cy.get('[data-test-id="publish-resource-btn"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains(contacts[1].fields.first_name);
    cy.contains(contacts[2].fields.first_name);
    cy.contains(contacts[3].fields.first_name);
  });
});
