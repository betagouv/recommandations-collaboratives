describe('I can follow the external resource tutorial', () => {
  it('displays the launcher tutorial on the external resource', () => {
    cy.login('conseiller1');
    cy.visit('/project/27/actions');
    cy.get("[data-test-id='create-task-button']").click();
    cy.get("[data-cy='radio-push-reco-external-resource']").check({
      force: true,
    });
    cy.get('[data-test-id="tutorial-project-launcher"]').should.exist;
  });
});
