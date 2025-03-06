describe('I can see a draft resource as a switchtender', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('sees a draft resource', () => {
    cy.visit('/ressource/3/');
  });
});
