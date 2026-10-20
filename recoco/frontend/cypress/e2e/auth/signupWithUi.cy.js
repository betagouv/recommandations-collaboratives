import project from '../../fixtures/projects/project.json';

describe('The Signup Page @inscription', () => {
  const userToSignup = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=org_name]': 'Signup Corp',
    '[name=role]': 'Tester',
    '[name=email]': 'signup4@success.test',
    '[name=phone]': '0102030405',
    '[name=password1]': 'Recoco2000',
    '[name=password2]': 'Recoco2000',
  };

  it('signup a new user', function () {
    cy.createProject('Test signup', project, true, userToSignup);
  });

  it('cannot signup without creating a projet', function () {
    cy.visit('accounts/signup/');
    cy.get('form').should('not.exist');
  });
});
