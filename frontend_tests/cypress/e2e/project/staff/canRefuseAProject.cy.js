describe('I can go to the dashboard and see the pending projects, and refuse one', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('refuses a project', () => {
    cy.visit('/projects/moderation');
    cy.contains('projet entrant à examiner');
    cy.contains('Friche à refuser');
    cy.get('[data_test_id="refuse-project"]')
      .contains('Refuser')
      .click({ force: true });
    cy.url().should('include', '/projects/moderation/');
    cy.contains('Friche à refuser').should('not.exist');
  });
});
