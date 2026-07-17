describe('I cannot access conversation without join project @page-projet-conversations', () => {
  beforeEach(() => {
    cy.login('conseiller3');
  });

  it('cant goes to public notes ', () => {
    cy.visit(`/project/29/`);

    cy.get('[data-test-id="project-navigation-conversations-new"]').should(
      'have.attr',
      'disabled'
    );
  });
});
