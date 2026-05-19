describe('I can see an expired resource as a switchtender @acces-ressources', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('sees an expired resource', () => {
    cy.visit('/ressource/3/');

    cy.get("[data-test-id='expired-resource-banner']").should('exist');
  });
});
