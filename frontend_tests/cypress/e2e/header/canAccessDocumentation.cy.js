describe('I can access documentation', () => {
  it('displays as staff member', () => {
    cy.login('staff');
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get('[data-test-id="documentation-button-staff"]')
      .invoke('attr', 'href')
      .then((url) => {
        cy.request(url).then((response) => {
          expect(response.status).to.eq(200);
        });
      });
  });

  it('displays as advisor', () => {
    cy.login('conseiller1');
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get('[data-test-id="documentation-button-advisor"]')
      .invoke('attr', 'href')
      .then((url) => {
        cy.request(url).then((response) => {
          expect(response.status).to.eq(200);
        });
      });
  });

  it('cannnot displays it', () => {
    cy.login('collectivité1');
    cy.get('[data-test-id="open-dropdown-profil-option-button"]').click({
      force: true,
    });
    cy.contains('Documentation').should('not.exist');
  });
});
