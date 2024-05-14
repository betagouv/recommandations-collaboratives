describe('I can follow a project', () => {
  beforeEach(() => {
    cy.login('bob');
  });

  it('goes to the homepage and create a project with the main CTA', () => {
    cy.createProject('fake project name');
  });
});
