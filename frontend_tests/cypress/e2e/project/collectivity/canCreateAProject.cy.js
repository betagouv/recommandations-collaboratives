describe('I can follow a project @deposer-projet', () => {
  it('goes to the homepage and create a project with the main CTA', () => {
    cy.login('collectivité1');
    cy.createProject('fake project name');
  });
});
