describe('I can go to the dashboard and see the pending projects, and approve one', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('approves a project', () => {
    cy.visit('/projects/moderation');
    cy.contains('Friche numéro 4')
      .closest("[data-test-id='project-card']")
      .find('[data-test-id="accept-project"]')
      .contains('Accepter')
      .click({ force: true });

    cy.url().should('include', '/project/');
    cy.contains('Friche numéro 4');

    cy.visit('/projects/moderation');
    cy.get('[data-test-id="moderation-page"]').should(
      'not.include.text',
      'Friche numéro 4'
    );
  });
});
