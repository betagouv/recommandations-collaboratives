describe('I can see an expired resource as a switchtender', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('sees an expired resource', () => {
    cy.visit('/ressource/3/');

    cy.get("[data-test-id='expired-resource-banner']").should('exist');
  });
});
