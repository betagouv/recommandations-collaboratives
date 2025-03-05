describe('I can read only overview page', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to the overview page and not see the advisor note', () => {
    cy.visit(`/project/29`);

    cy.contains('Note interne').should('not.exist');
  });
});
