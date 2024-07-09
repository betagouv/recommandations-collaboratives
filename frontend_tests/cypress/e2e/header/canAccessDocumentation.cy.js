describe('I can access documentation', () => {
  it('displays as staff member', () => {
    cy.login('staff');
    cy.hideCookieBannerAndDjango();
    cy.visit(`/`);
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get('[data-test-id="documentation-button-staff"]').click({
      force: true,
    });
    cy.url().should('include', 'pour-les-administrateurs-dun-portail');
    // cy.visit(`/`);
    // cy.logout();
  });

  xit('displays as advisor', () => {
    cy.login('jean');
    cy.hideCookieBannerAndDjango();
    cy.visit(`/`);
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get('[data-test-id="documentation-button-advisor"]').click({
      force: true,
    });
    cy.url().should(
      'include',
      'pour-les-acteurs-publics-qui-conseillent-les-collectivites'
    );
    // cy.visit(`/`);
    // cy.logout();
  });

  it('cannnot displays it', () => {
    cy.login('bob');
    cy.hideCookieBannerAndDjango();
    cy.visit(`/`);
    cy.get('[data-test-id="open-dropdown-profil-option-button"]').click({
      force: true,
    });
    cy.contains('Documentation').should('not.exist');
    // cy.logout();
  });
});
