describe('I can create a project as a collectivity', () => {
  it('finds the content "type"', () => {
    cy.visit('/')
    cy.get('a').should('have.class', 'fr-btn fr-text--xl custom-button').contains('Solliciter UrbanVitaliz').click({ force: true })

    cy.url().should('include', '/onboarding/')

    cy.get('#id_first_name')
      .type('fakefirstname', { force: true })
      .should('have.value', 'fakefirstname')

    cy.get('#id_last_name')
      .type('fakelastname', { force: true })
      .should('have.value', 'fakelastname')

    cy.get('#id_email')
      .type('fake@email.com', { force: true })
      .should('have.value', 'fake@email.com')

    cy.get('#id_phone')
      .type('010101010101', { force: true })
      .should('have.value', '010101010101')

    cy.get('#id_org_name')
      .type('fake structure', { force: true })
      .should('have.value', 'fake structure')

    cy.get('#id_name')
      .type('fake project name', { force: true })
      .should('have.value', 'fake project name')

    cy.get('#input-project-address')
      .type('143 rue fake', { force: true })
      .should('have.value', '143 rue fake')

    cy.get('[name=postcode]')
      .type('30130', { force: true })
      .should('have.value', '30130')

    cy.get('#input-project-description')
      .type('Fake project description', { force: true })
      .should('have.value', 'Fake project description')

    cy.get('#id_response_1')
      .type('Fake project description precision', { force: true })
      .should('have.value', 'Fake project description precision')

    cy.get('#id_response_2_0')
      .check({ force: true })

    cy.document().then((doc) => {
      var iframe = doc.getElementById('id_captcha').querySelector('iframe');
      var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
      innerDoc.querySelector('.recaptcha-checkbox').click()
    })

    cy.wait(500)

    cy.contains('Envoyer ma demande').click({force:true});

    cy.url().should('include', '/accounts/login/')
  })
})
