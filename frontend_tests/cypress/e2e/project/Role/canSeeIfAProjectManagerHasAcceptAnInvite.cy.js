describe('I can go to a project and see if the main collaborator has accepted the invitation', () => {

  it('can see if the main colloborator has accepted the invitation or not', () => {
    cy.login('jean');
    cy.visit('/project/27/presentation');
    cy.get('[data-test-id="invite-not-accepted-banner"]').should('exist');

    cy.visit('/project/23/presentation');
    cy.get('[data-test-id="invite-not-accepted-banner"]').should('not.exist');
  });
});
