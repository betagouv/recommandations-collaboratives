describe('I can go to the dashboard and see the pending projects, and approve one', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('approves a project', () => {
    cy.visit('/projects/moderation');
    cy.contains('projet entrant à examiner');
    cy.contains('Friche numéro 4');
    cy.get('[data_test_id="accept-project"]')
      .contains('Accepter')
      .click({ force: true });
    cy.url().should('include', '/project/');
    cy.contains('Friche numéro 4');

    cy.visit('/projects/moderation');
    cy.contains('Friche numéro 4').should('not.exist');
  });
});
