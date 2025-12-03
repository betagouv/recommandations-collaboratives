describe('I can create a new project as a new user', () => {
  const projectInfo = {
    name: 'Test Project',
    location: '123 Test Street',
    postcode: 42424,
    insee: 42123,
    commune: 'commune de test',
    description: 'This is a test project description',
    email: `${Date.now()}@example.com`,
    fixedEmail: 'test2@example.com',
  };

  const signupInfo = {
    first_name: 'Test',
    last_name: 'User',
    organization: 'Test Organization',
    organization_position: 'Test Position',
    phone_no: '0102030405',
    password1: 'Testpassword123',
    password2: 'Testpassword123',
  };

  const alreadyExistingUserInfo = {
    email: projectInfo.email,
    password: 'Testpassword123',
  };

  it('goes through the complete onboarding process', () => {
    // Visit home page and click on need help button
    cy.visit('/');
    cy.get('[data-test-id="button-need-help"]')
      .contains('Solliciter')
      .click({ force: true });

    // Land on onboarding/project page
    cy.url().should('include', '/onboarding/project');

    // Fill project form
    cy.get('#id_name')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.name, { delay: 0 })
      .should('have.value', projectInfo.name)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_location')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.location, { delay: 0 })
      .should('have.value', projectInfo.location)
      .should('have.class', 'fr-input--valid');

    cy.get('[data-test-id="input-postcode"]')
      .type(projectInfo.postcode, { delay: 0 })
      .should('have.value', projectInfo.postcode)
      .parent()
      .should('have.class', 'fr-input-group--valid');

    cy.get('[data-test-id="select-city"]')
      .should('not.have.class', 'fr-select-group--error')
      .focus();

    cy.get('[data-test-id="select-city"]')
      .should('contain.text', projectInfo.commune)
      .should('have.value', projectInfo.insee)
      .parent()
      .should('have.class', 'fr-select-group--valid');

    cy.get('#id_description')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.description, { delay: 0 })
      .should('have.value', projectInfo.description)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_email')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.email, { delay: 0 })
      .should('have.value', projectInfo.email)
      .should('have.class', 'fr-input--valid');

    // Handle captcha
    cy.document().then((doc) => {
      const iframe = doc.getElementById('id_captcha').querySelector('iframe');
      const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
      innerDoc.querySelector('.recaptcha-checkbox').click();
      cy.wait(400);
    });

    // Submit project form
    cy.get('button[type="submit"]').click();

    // Land on onboarding/signup page
    cy.url().should('include', '/onboarding/signup');

    // Fill signup form
    cy.get('[name=first_name]')
      .type(signupInfo.first_name, { delay: 0 })
      .should('have.value', signupInfo.first_name);

    cy.get('[name=last_name]')
      .type(signupInfo.last_name, { delay: 0 })
      .should('have.value', signupInfo.last_name);

    cy.get('[name=org_name]')
      .type(signupInfo.organization, { delay: 0 })
      .should('have.value', signupInfo.organization);

    cy.get('[name=role]')
      .type(signupInfo.organization_position, { delay: 0 })
      .should('have.value', signupInfo.organization_position);

    cy.get('[name=phone]')
      .type(signupInfo.phone_no, { delay: 0 })
      .should('have.value', signupInfo.phone_no);

    cy.get('[name=password]').type('nope', { delay: 0 });

    cy.get('[id="error_0_password"]').should('be.visible'); // min length error
    cy.get('[id="error_1_password"]').should('be.visible'); // number error
    cy.get('[id="error_2_password"]').should('be.visible'); // uppercase error

    cy.get('[name=password]').clear();

    cy.get('[name=password]')
      .type(signupInfo.password1, { delay: 0 })
      .should('have.value', signupInfo.password1);

    cy.get('[id="valid_0_password"]').should('be.visible'); // min length error
    cy.get('[id="valid_1_password"]').should('be.visible'); // number error
    cy.get('[id="valid_2_password"]').should('be.visible'); // uppercase error

    // Submit signup form
    cy.get('[type=submit]').click();

    // Land on onboarding/summary page
    cy.url().should('include', '/onboarding/summary');
  });

  it('goes through the onboarding process but stop at signup page', () => {
    // Visit home page and click on need help button
    cy.visit('/');
    cy.get('[data-test-id="button-need-help"]')
      .contains('Solliciter')
      .click({ force: true });

    // Land on onboarding/project page
    cy.url().should('include', '/onboarding/project');

    // Fill project form
    cy.get('#id_name')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.name, { delay: 0 })
      .should('have.value', projectInfo.name)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_location')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.location, { delay: 0 })
      .should('have.value', projectInfo.location)
      .should('have.class', 'fr-input--valid');

    cy.get('[data-test-id="input-postcode"]')
      .type(projectInfo.postcode, { delay: 0 })
      .should('have.value', projectInfo.postcode)
      .parent()
      .should('have.class', 'fr-input-group--valid');

    cy.get('[data-test-id="select-city"]')
      .should('not.have.class', 'fr-select-group--error')
      .focus();

    cy.get('[data-test-id="select-city"]')
      .should('contain.text', projectInfo.commune)
      .should('have.value', projectInfo.insee)
      .parent()
      .should('have.class', 'fr-select-group--valid');

    cy.get('#id_description')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.description, { delay: 0 })
      .should('have.value', projectInfo.description)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_email')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.fixedEmail, { delay: 0 })
      .should('have.value', projectInfo.fixedEmail)
      .should('have.class', 'fr-input--valid');

    // Handle captcha
    cy.document().then((doc) => {
      const iframe = doc.getElementById('id_captcha').querySelector('iframe');
      const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
      innerDoc.querySelector('.recaptcha-checkbox').click();
      cy.wait(400);
    });

    // Submit project form
    cy.get('button[type="submit"]').click();

    // Land on onboarding/signup page
    cy.url().should('include', '/onboarding/signup');

    // Restart at project page
    cy.visit('/onboarding/project');

    cy.get('[data-cy="found-email-onboarding"]').should(
      'contain.text',
      projectInfo.fixedEmail
    );

    cy.get('[data-cy="continue-onboarding"]').click();

    // Fill signup form
    cy.get('[name=first_name]')
      .type(signupInfo.first_name, { delay: 0 })
      .should('have.value', signupInfo.first_name);

    cy.get('[name=last_name]')
      .type(signupInfo.last_name, { delay: 0 })
      .should('have.value', signupInfo.last_name);

    cy.get('[name=org_name]')
      .type(signupInfo.organization, { delay: 0 })
      .should('have.value', signupInfo.organization);

    cy.get('[name=role]')
      .type(signupInfo.organization_position, { delay: 0 })
      .should('have.value', signupInfo.organization_position);

    cy.get('[name=phone]')
      .type(signupInfo.phone_no, { delay: 0 })
      .should('have.value', signupInfo.phone_no);

    cy.get('[name=password]')
      .type(signupInfo.password1, { delay: 0 })
      .should('have.value', signupInfo.password1);

    // Submit signup form
    cy.get('[type=submit]').click();

    // Land on onboarding/summary page
    cy.url().should('include', '/onboarding/summary');
  });

  it('goes through the complete onboarding process with already existing user', () => {
    // Visit home page and click on need help button
    cy.visit('/');
    cy.get('[data-test-id="button-need-help"]')
      .contains('Solliciter')
      .click({ force: true });

    // Land on onboarding/project page
    cy.url().should('include', '/onboarding/project');

    // Fill project form
    cy.get('#id_name')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.name, { delay: 0 })
      .should('have.value', projectInfo.name)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_location')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.location, { delay: 0 })
      .should('have.value', projectInfo.location)
      .should('have.class', 'fr-input--valid');

    cy.get('[data-test-id="input-postcode"]')
      .type(projectInfo.postcode, { delay: 0 })
      .should('have.value', projectInfo.postcode)
      .parent()
      .should('have.class', 'fr-input-group--valid');

    cy.get('[data-test-id="select-city"]')
      .should('not.have.class', 'fr-select-group--error')
      .focus();

    cy.get('[data-test-id="select-city"]')
      .should('contain.text', projectInfo.commune)
      .should('have.value', projectInfo.insee)
      .parent()
      .should('have.class', 'fr-select-group--valid');

    cy.get('#id_description')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.description, { delay: 0 })
      .should('have.value', projectInfo.description)
      .should('have.class', 'fr-input--valid');

    cy.get('#id_email')
      .should('not.have.class', 'fr-input--error')
      .type(projectInfo.email, { delay: 0 })
      .should('have.value', projectInfo.email)
      .should('have.class', 'fr-input--valid');

    // Handle captcha
    cy.document().then((doc) => {
      const iframe = doc.getElementById('id_captcha').querySelector('iframe');
      const innerDoc = iframe.contentDocument || iframe.contentWindow.document;
      innerDoc.querySelector('.recaptcha-checkbox').click();
      cy.wait(400);
    });

    // Submit project form
    cy.get('button[type="submit"]').click();

    // Land on onboarding/signup page
    cy.url().should('include', '/onboarding/signin');

    // Fill signup form
    cy.get('[name=login]').should('have.value', alreadyExistingUserInfo.email);

    cy.get('[name=password]')
      .type(alreadyExistingUserInfo.password, { delay: 0 })
      .should('have.value', alreadyExistingUserInfo.password);

    // Submit signup form
    cy.get('[type=submit]').click();

    // Land on onboarding/summary page
    cy.url().should('include', '/onboarding/summary');
  });
});
