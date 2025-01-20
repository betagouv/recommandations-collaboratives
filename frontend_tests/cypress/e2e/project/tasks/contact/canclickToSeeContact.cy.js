describe('I can see contacts information', () => {
  beforeEach(() => {
    cy.login('bob');
  });

  it('click to see contat info and doesnt have to click again', () => {
    cy.visit(`/ressource/2`);
    cy.get('[data-test-id="see-contact-info-button"]').each(($button)=>{cy.wrap($button).click({ force: true })});
    cy.get('[data-test-id="see-contact-info-button"]').should('not.be.visible');
    cy.visit(`/ressource/2`);
    cy.get('[data-test-id="see-contact-info-button"]').should('not.be.visible');
  });

});
