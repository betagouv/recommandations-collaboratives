describe('I can see CTA on survey page', () => {
  it('should display CTA as collectivity', () => {
    cy.login('collectivité1');
    cy.visit(`/project/2/connaissance`);
    cy.get('[data-test-id="link-fill-survey-cta"]').should('be.visible');
  });

  it('should not display CTA as staff', () => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit(`/project/2/connaissance`);
    cy.get('[data-test-id="link-fill-survey-cta"]').should('not.exist');
  });

  it('should not display CTA as staff', () => {
    cy.login('conseiller1');
    cy.visit(`/project/2/connaissance`);
    cy.get('[data-test-id="link-fill-survey-cta"]').should('not.exist');
  });
});
