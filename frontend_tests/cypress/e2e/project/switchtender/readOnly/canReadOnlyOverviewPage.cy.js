describe('I can read only overview page', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('goes to overview and read only content', () => {
    cy.visit(`/project/29`);

    cy.url().should('include', '/presentation');

    cy.contains('Note interne aux conseillers').should('not.exist');
  });
});
