describe('I can go to the dashboard and see the pending demand for advising, and manage one', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('approves a national advisor ', () => {
    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-view"]').click({
      force: true,
    });

    cy.contains('nationalAdvisorRequest@test.fr')
      .closest("[data-test-id='moderation-advisor-card']")
      .find('[data-test-id="accept-advisor-access"]')
      .click();

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

    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-account-moderation-page"]').should(
      'not.include.text',
      'refuseAdvisorRequest@test.fr'
    );
  });

  it('modify then accept a regional advisor', () => {
    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-view"]').click({
      force: true,
    });

    cy.contains('regionalAdvisorRequest@test.fr')
      .closest("[data-test-id='moderation-advisor-card']")
      .find('[data-test-id="modify-advisor-access"]')
      .click();

    cy.get('[data-test-id="remove-selected-item"]').first().click();

    cy.get('[data-test-id="save-modif-departments"]').click();

    cy.get('[data-test-id="moderation-advisor-card"]')
      .find('[data-test-id="department-ask-for-access-advisor"]')
      .should('have.length', 1);

    cy.contains('regionalAdvisorRequest@test.fr')
      .closest("[data-test-id='moderation-advisor-card']")
      .find('[data-test-id="accept-advisor-access"]')
      .click();

    // Check that the advisor is now in the list of advisors (NOT WORKING ON PROD)
    // cy.visit('/crm/users/?username=regionalAdvisor&role=1&ordering=');
    // cy.contains('NationalAdvisor');

    cy.visit('/projects/moderation');
    cy.get('[data-test-id="advisor-account-moderation-page"]').should(
      'not.include.text',
      'regionalAdvisorRequest@test.fr'
    );
  });
});
