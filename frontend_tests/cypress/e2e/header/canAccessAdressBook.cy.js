describe('I can access to my address book', () => {
  beforeEach(() => {
    cy.login('staff'); // TODO replace by staffOnSite and check behaviour
  });

  it('', () => {
    cy.visit(`/`);
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get("[data-test-id='button-address-book']").click({ force: true });
    cy.url().should('include', '/addressbook/contacts');
  });
});

describe("I can't see adress book because I don't have one", () => {
  beforeEach(() => {
    cy.login('conseiller1');
  });

  it('', () => {
    cy.visit(`/`);
    cy.get('[data-test-id="open-dropdown-profil-option-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="button-address-book"]').should('not.exist');
  });
});
