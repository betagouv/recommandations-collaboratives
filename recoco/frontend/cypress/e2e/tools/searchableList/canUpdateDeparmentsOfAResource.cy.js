describe('I can assign new deparments when I edit a resource @acces-ressources', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to edit a resource and assign a new deparment', () => {
    cy.visit('/ressource/1/');
    cy.get('[data-test-id="edit-resource"]').click();

    cy.get('[data-test-id="open-multiselect"]').click({ force: true });

    cy.get('[id="department-1"]').click({ force: true });
    cy.get('[data-test-id="publish-resource-btn"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains('Département de test numéro 2');
  });
});
