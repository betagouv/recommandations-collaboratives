describe('I can go to CRM and toggle project impact tag', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
    cy.visit('/crm/project');
    cy.contains('Friche numéro 1').click();
  });

  it('toggle on an impact tag', () => {
    cy.contains('A nice tag').parent().find('input').should('not.be.checked');
    cy.contains('Another nice tag')
      .parent()
      .find('input')
      .should('not.be.checked');
    cy.contains('A nice tag').click();
    cy.contains('A nice tag').parent().find('input').should('be.checked');
    cy.contains('Another nice tag')
      .parent()
      .find('input')
      .should('not.be.checked');
  });

  it('toggle on an impact tag', () => {
    cy.contains('A nice tag').parent().find('input').should('be.checked');
    cy.contains('Another nice tag')
      .parent()
      .find('input')
      .should('not.be.checked');
    cy.contains('A nice tag').click();
    cy.contains('A nice tag').parent().find('input').should('not.be.checked');
    cy.contains('Another nice tag')
      .parent()
      .find('input')
      .should('not.be.checked');
  });
});
