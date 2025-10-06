describe('The Signup Page', () => {
  const userToSignup = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=organization]': 'Signup Corp',
    '[name=organization_position]': 'Tester',
    '[name=email]': 'signup3@success.test',
    '[name=phone_no]': '0102030405',
    '[name=password1]': 'Coco2000',
    '[name=password2]': 'Coco2000',
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
    cy.document().then((doc) => {
      var iframe = doc.getElementById('id_captcha').querySelector('iframe');
      var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
      innerDoc.querySelector('.recaptcha-checkbox').click();
      cy.wait(400);
      cy.get('[type=submit]').click();

      cy.location().should((loc) => {
        expect(loc.pathname).to.eq('/');
      });
    });
  });
});
