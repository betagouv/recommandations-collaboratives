describe('I can access to my adress book', () => {
  beforeEach(() => {
    cy.login('staff');
  });

  it('', () => {
    cy.visit(`/`);
    cy.get("[data-test-id='open-dropdown-profil-option-button']").click({
      force: true,
    });
    cy.get("[data-test-id='button-adress-book']").click({ force: true });
    cy.url().should('include', '/addressbook/organizations');
  });
});

describe("I can't see adress book because I don't have one", () => {
  beforeEach(() => {
    cy.login('jean');
  });

  it('', () => {
    cy.visit(`/`);
    cy.get('[data-test-id="open-dropdown-profil-option-button"]').click({
      force: true,
    });
    cy.get('[data-test-id="button-adress-book"]').should('not.exist');
  });
});
