describe("I can create a project if i'm connected", () => {
  beforeEach(() => {
    cy.login('bob');
    cy.acceptCookies();
  });

  it('goes to the onboarding process step by step and create a project ', () => {
    cy.createProject('Coucou');
  });
});
