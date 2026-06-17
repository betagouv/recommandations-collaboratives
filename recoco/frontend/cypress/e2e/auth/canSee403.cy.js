describe('I can access to 403 page when cannot access to the page @error-page', () => {
  it('should show relogin url on custom 403 page when authenticated', () => {
    cy.login('collectivité1');
    cy.visit('/project/10/presentation', { failOnStatusCode: false });
    cy.get('[data-test-id="technicat-info"]').should('be.visible');
    cy.get('[data-test-id="link-relogin-403"]').should('be.visible');
  });
});
