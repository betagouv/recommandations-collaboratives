describe('I can go to the dashboard and see the pending demand for advising, and manage one', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('approves a national advisor ', () => {
    sessionStorage.setItem('view', 'advisor');
    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-view"]').click({
      force: true,
    });

    cy.contains('nationalAdvisorRequest@test.fr')
      .closest("[data-test-id='moderation-advisor-card']")
      .find('[data-test-id="accept-advisor-access"]')
      .click();

    // Check that the advisor is now in the list of advisors (NOT WORKING ON PROD)
    // cy.visit('/crm/users/?username=NationalAdvisor&role=1&ordering=');
    // cy.contains('NationalAdvisor');

    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-account-moderation-page"]').should(
      'not.include.text',
      'nationalAdvisorRequest@test.fr'
    );
  });

  it('refuses an advisor', () => {
    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-view"]').click({
      force: true,
    });

    cy.contains('refuseAdvisorRequest@test.fr')
      .closest("[data-test-id='moderation-advisor-card']")
      .find('[data-test-id="refuse-advisor-access"]')
      .click();

    // Check that the advisor is now in the list of advisors (NOT WORKING ON PROD)
    // cy.visit('/crm/users/?username=refuseAdvisor&role=1&ordering=');
    // cy.not.contains('refuseAdvisor');

    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-account-moderation-page"]').should(
      'not.include.text',
      'refuseAdvisorRequest@test.fr'
    );
  });

  xit('modify then accept a regional advisor', () => {
    // data-test-id="modify-advisor-access"
  });
});
