describe('I can read only public notes', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('cant goes to public notes ', () => {
    cy.visit(`/project/29/`);

    cy.get('[data-test-id="project-navigation-conversations"]').should(
      'be.disabled'
    );
  });
});
