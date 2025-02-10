describe('I can not see owner contact', () => {
  it('display owner contact (as staff)', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="container-revealed-contact"]').should(
      'contains.text',
      'bob@test.fr'
    );
  });

  it('display owner contact (as owner)', () => {
    cy.login('bob');
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="container-revealed-contact"]').should(
      'contains.text',
      'bob@test.fr'
    );
  });

  it('display hiden owner contact (as advisor)', () => {
    cy.login('conseiller1');
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="container-revealed-contact"]').should('not.be.visible');
    cy.get('[data-cy="btn-overview-reveal-contact"]').click();
    cy.get('[data-cy="container-revealed-contact"]').should(
      'contains.text',
      'bob@test.fr'
    );
    cy.reload();
    cy.get('[data-cy="container-revealed-contact"]').should(
      'contains.text',
      'bob@test.fr'
    );
  });
});
