import contacts from '../../../fixtures/addressbook/contacts.json';

describe('I can assign some contacts when I create a resource @acces-ressources', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to create a resource and assign 3 contacts', () => {
    cy.visit('/ressource/create/');

    cy.get('#id_title')
      .type('Ressource de test', { force: true })
      .should('have.value', 'Ressource de test');

    cy.get('#id_subtitle')
      .type('Soustitre de la ressource de test', { force: true })
      .should('have.value', 'Soustitre de la ressource de test');

    cy.get('#id_summary')
      .type('résumé de la ressource de test', { force: true })
      .should('have.value', 'résumé de la ressource de test');

    cy.get('#id_tags')
      .type('etiquette1', { force: true })
      .should('have.value', 'etiquette1');

    cy.get('#search-contact-input')
      .type('lala', { force: true })
      .should('have.value', 'lala');
    cy.get('[data-test-id="contact-card-component"]')
      .first()
      .click({ force: true });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    cy.wait(500);

    cy.get('#search-contact-input')
      .type('lili', { force: true })
      .should('have.value', 'lili');
    cy.get('[data-test-id="contact-card-component"]')
      .contains('lili')
      .click({ force: true });
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });

    cy.get('#id_expires_on')
      .type('2022-12-20', { force: true })
      .should('have.value', '2022-12-20');

    cy.get('.ProseMirror p').click();
    cy.focused().type('text', 'contenu de la ressource de test');

    cy.get('[data-test-id="publish-resource-btn"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains('Ressource de test');
    cy.contains('résumé de la ressource de test');

    cy.contains(contacts[1].fields.first_name);
    cy.contains(contacts[2].fields.first_name);
  });
});
