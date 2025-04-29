describe('I can create a resource as a switchtender', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('creates a resource', () => {
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

    cy.get('#id_expires_on')
      .type('20/12/2022', { force: true })
      .should('have.value', '20/12/2022');

    cy.get('.ProseMirror p').click();
    cy.focused().type('text', 'test from ressource description');

    // cy.get('[data-cy="button-ressource-create"]').click({ force: true });
    cy.get('[data-cy="form-resource-create"]').submit();

    cy.url().should('include', '/ressource/');

    cy.contains('Ressource de test');
    cy.contains('résumé de la ressource de test');
  });
});
