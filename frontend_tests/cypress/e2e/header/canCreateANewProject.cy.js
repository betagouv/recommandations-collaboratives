describe('I can create a new project from the main header project list dropdown', () => {
  it('display button as a collectivity', () => {
    cy.login('collectivité1');
    cy.visit(`/`);
    cy.get('[data-test-id="create-project"]')
      .should('exist')
      .click({ force: true });
    cy.url().should('include', '/onboarding');
  });

  it("don't display button as an advisor", () => {
    cy.login('conseiller1');
    cy.visit(`/`);
    cy.get('[data-test-id="create-project"]').should('not.exist');
  });
});
