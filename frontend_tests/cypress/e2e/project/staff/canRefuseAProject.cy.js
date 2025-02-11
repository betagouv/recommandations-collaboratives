describe('I can go to the dashboard and see the pending projects, and refuse one', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('refuses a project', () => {
    cy.visit('/projects/moderation');

    cy.contains('Friche à refuser')
      .closest("[data-test-id='project-card']")
      .find('[data-test-id="refuse-project"]')
      .contains('Refuser')
      .click();

    cy.url().should('include', '/projects/moderation/');

    cy.get('[data-test-id="moderation-page"]').should(
      'not.include.text',
      'Friche à refuser'
    );
  });
});
