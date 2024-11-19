describe('I can follow a project', () => {
  it('goes to the homepage and create a project with the main CTA', () => {
    cy.login('collectivité1');
    cy.createProject('fake project name');
  });
});
