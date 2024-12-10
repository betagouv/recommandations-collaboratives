describe('The Signup Page', () => {
  const userToSignup = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=organization]': 'Signup Corp',
    '[name=organization_position]': 'Tester',
    '[name=email]': 'signup@success.test',
    '[name=phone_no]': '0102030405',
    '[name=password1]': 'derpderp',
    '[name=password2]': 'derpderp',
  };

  it('signup a new user', function () {
    cy.visit('accounts/signup/');

    cy.url().should('include', '/accounts/signup/');

    for (const key in userToSignup) {
      if (Object.prototype.hasOwnProperty.call(userToSignup, key)) {
        const element = userToSignup[key];
        cy.get(key).type(element, { delay: 0 });
      }
    }

    cy.clickRecaptcha();

    cy.get('[type=submit]').click();

    cy.location().should((loc) => {
      expect(loc.pathname).to.eq('/');
    });
  });
});
