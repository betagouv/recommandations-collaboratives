describe('I can go to overview tab and check invitation project member button', () => {
  it('shows disabled button to invite new project member', () => {
    cy.login('national');
    cy.visit('/project/1/presentation');
    cy.get('[data-cy="invite-project-member-button"]').should('be.disabled');
  });
});
