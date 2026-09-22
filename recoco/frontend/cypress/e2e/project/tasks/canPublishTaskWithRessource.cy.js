describe('I can attach miscellanious ressource to task @page-projet-recommandations-creation @page-projet-recommandations', () => {
  it('publishes a recommendation with a resource', () => {
    cy.login('conseiller1');

    cy.visit(`/projects/action/?project_id=25&resource_id=2`);

    cy.get('[data-cy="radio-push-reco-single-resource"]').should('be.checked');
    cy.get('[data-test-id="publish-draft-task-button"]').should('be.enabled');
    cy.get('[data-cy="button-submit-task"]').should('be.enabled');

    cy.typeInTiptapEditor('reco test from action description');

    cy.get('[data-cy="button-submit-task"]').should('be.enabled').click();

    cy.url().should('include', '/conversations');
  });

  it('cannot select a draft resource and see warning', () => {
    cy.login('staff');
    cy.visit(`/projects/action/?project_id=25`);

    cy.get('[data-cy="radio-push-reco-single-resource"]').should('be.checked');

    cy.get('[data-test-id="search-resource-input"]').type('brouillon', {
      delay: 0,
    });
    cy.get('[data-cy="resource-warning-status-draft"]').should('be.visible');
    cy.get('[data-cy="radio-resource-list-task"]')
      .first()
      .should('be.disabled');
  });

  xit('publishes a task with external resource', () => {
    cy.login('conseiller1');
    cy.visit(`/projects/action/?project_id=25`);

    cy.get('[data-cy="radio-push-reco-external-resource"]')
      .should('not.be.checked')
      .check({ force: true })
      .should('be.checked');

    cy.get('[data-cy="input-external-resource-url"]').type(
      'https://wiki.resilience-territoire.ademe.fr/wiki/Comment_partager_la_connaissance_et_documentation_dans_le_commun_%3F',
      { force: true, delay: 0 }
    );
    cy.get('[data-cy="button-external-resource-load"]').click();
    cy.get('[data-cy="radio-resource-list-task"]').check({ force: true });

    cy.typeInTiptapEditor('reco test from action description');

    cy.get('[data-cy="button-submit-task"]').should('be.enabled').click();

    cy.url().should('include', '/conversations');
  });

  it('publishes a recommendation with no resource', () => {
    cy.login('conseiller1');
    cy.visit(`/projects/action/?project_id=25`);

    cy.get('[data-cy="radio-push-reco-no-resource"]')
      .should('not.be.checked')
      .check({ force: true })
      .should('be.checked');

    cy.typeInTiptapEditor('reco test with no resource');

    cy.get('[data-cy="input-title-task"]').type('reco test with no resource', {
      delay: 0,
    });
    cy.get('[data-cy="button-submit-task"]').should('be.enabled').click();

    cy.url().should('include', '/conversations');
  });
});
