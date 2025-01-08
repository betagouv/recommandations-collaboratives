describe('I can not see owner contact', () => {
  it('display owner contact (as advisor)', () => {
    cy.login('conseiller1');
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="container-revealed-contact"]').should('not.be.visible');
    cy.get('[data-cy="btn-overview-reveal-contact"]').click();
    cy.get('[data-cy="container-revealed-contact"]').should(
      'contains.text',
      'bob@test.fr'
    );
  });
});
