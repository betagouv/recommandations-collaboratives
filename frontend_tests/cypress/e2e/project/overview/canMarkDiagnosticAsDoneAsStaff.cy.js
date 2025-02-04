describe('I can mark project diagnostic done ', () => {
  it('display diagnostic button (as staff)', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="button-diag-project-done"]').should('be.visible').click();
    cy.get('[data-cy="button-diag-project-done"]').should('not.exist');
    cy.get('[data-cy="diag-project-done"]').should('be.visible');
  });

  it('do not display diagnostic button (as owner)', () => {
    cy.login('bob');
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="button-diag-project-done"]').should('not.exist');
  });

  it('do not display diagnostic button (as advisor)', () => {
    cy.login('conseiller1');
    cy.visit(`/project/2/presentation`);
    cy.get('[data-cy="button-diag-project-done"]').should('not.exist');
  });
});
