import users from '../../fixtures/users/users.json';

describe('The Login Page', () => {
  let currentUser = {};

  beforeEach(() => {
    currentUser = users[1].fields;
  });

  it('sets auth cookie when logging in via form submission', function () {
    const { username } = currentUser;

    cy.visit('/accounts/login/');

    cy.url().should('include', '/accounts/login/');

    cy.get('#id_login')
      .type(username, { force: true })
      .should('have.value', username);

    cy.get('#id_password')
      .type('Coco2000', { force: true })
      .should('have.value', 'Coco2000');

    cy.get('[type=submit]').click({ force: true });

    cy.contains(`Connexion avec ${username} réussie.`);

    // // we should be redirected to /dashboard
    cy.url().should('include', '/projects');

    // // our auth cookie should be present
    cy.getCookie('sessionid').should('exist');
  });
});
