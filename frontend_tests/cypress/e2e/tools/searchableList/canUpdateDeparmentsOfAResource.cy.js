describe('I can assign new deparments when I edit a resource', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('goes to edit a resource and assign 3 new deparments', () => {
    cy.visit('/ressource/1/');
    cy.get('[data-test-id="edit-resource"]').click();

    cy.get('#id_departments-selected-list')
      .children()
      .eq('1')
      .children('span')
      .click({ force: true });

    cy.get('#id_departments-input').focus();
    cy.get('#id_departments-list').children().first('p').click({ force: true });

    cy.get('[type="submit"]').click({ force: true });

    cy.url().should('include', '/ressource/');

    cy.contains('Département de test');
  });
});
