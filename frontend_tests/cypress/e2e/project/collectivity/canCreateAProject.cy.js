describe('I can follow a project', () => {
  beforeEach(() => {
    cy.login('collectivité1');
  });

  it('goes to the homepage and create a project with the main CTA', () => {
    cy.createProject('fake project name');
  });
});
