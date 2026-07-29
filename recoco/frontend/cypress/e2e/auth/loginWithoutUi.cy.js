describe('I can access the Dashboard Page with a non UI login @connexion', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('should access the dashboard', () => {
    cy.visit('/');
  });
});
