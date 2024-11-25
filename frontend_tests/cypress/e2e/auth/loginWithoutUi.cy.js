describe('I can access the Dashboard Page with a non UI login', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('should access the dashboard', () => {
    cy.visit('/');
  });
});
