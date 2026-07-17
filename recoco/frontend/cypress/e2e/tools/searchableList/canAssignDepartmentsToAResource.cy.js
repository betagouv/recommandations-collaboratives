describe('I can assign some deparments when I create a resource @acces-ressources', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to create a resource and assign 2 deparments', () => {
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

    cy.get('#select-list-input').click();
    cy.get('label').contains('Département de test').click({ force: true });
    cy.get('label')
      .contains('Département de test numéro 2')
      .click({ force: true });

    cy.get('#id_expires_on').type('2022-12-20', { force: true });

    cy.get('.ProseMirror p').click();
    cy.focused().type('text', 'contenu de la ressource de test');

    cy.get('[data-test-id="publish-resource-btn"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains('Ressource de test');
    cy.contains('résumé de la ressource de test');

    cy.contains(
      'Cette ressource est disponible dans les départements suivants :'
    );
    cy.contains('Département de test');
    cy.contains('Département de test numéro 2');
  });
});
