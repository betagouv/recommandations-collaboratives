describe('I can access the Dashboard Page with a non UI login', () => {
  beforeEach(() => {
    cy.login("bob");
    cy.createProject(3);
  })

  it("should access the dashboard", () => {
    cy.visit('/')
  });
})
