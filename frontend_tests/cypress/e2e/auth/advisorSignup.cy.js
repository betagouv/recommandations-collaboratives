describe('Signup advisor @demande-compte-conseiller', () => {
  const userToSignup = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=organization]': 'Signup Corp',
    '[name=organization_position]': 'Tester',
    '[name=email]': 'signup4@success.test',
    '[name=phone_no]': '0102030405',
    '[name=password1]': 'derpderp',
    '[name=password2]': 'derpderp',
  };

  it('signup a new advisor', function () {
    cy.visit('/acteurs-locaux');
    cy.get('[data-test-id="button-advisor-access-request"]').click();

    cy.url().should('include', '/advisor-access-request');

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
      cy.wait(500);
      cy.get('[type=submit]').click();

      cy.location().should((loc) => {
        expect(loc.pathname).to.eq('/advisor-access-request');
      });

      cy.get('[type=submit]').click();
      cy.url().should('include', '/advisor-access-request');

      cy.get('[name="comment"]').type("Tester c'est douter");
      cy.get('[type=submit]').click();

      cy.get('[data-test-id="pending-advisor-request-confirmation"]').should(
        'be.visible'
      );
    });
  });
});
