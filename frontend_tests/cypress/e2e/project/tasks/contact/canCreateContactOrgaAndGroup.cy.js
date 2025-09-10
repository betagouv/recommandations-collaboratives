describe('I can create and edit a contact and an organization on contactbook', () => {
  beforeEach(() => {
    cy.login('staff');
    cy.get('[data-test-id="button-consent-accept-all"]').click({ force: true });
  });

  it('can create a contact and create a new organization with no group and no departments', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('Anakin');
    cy.get('[data-test-id="last-name"]').type('Skywalker');
    cy.get('[data-test-id="email"]').type('anakin.skywalker@jedicorp.com');
    //search for a non existing organization
    cy.get('#search-organization-input').type('jedicorp');
    //click on create organization button
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    //create the organization
    cy.get('[data-test-id="button-create-new-organization"]').click();
    //add job title
    cy.get('[data-test-id="job"]').type('Jedi Knight');
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should(
      'contain',
      'Anakin Skywalker'
    );
  });

  it('can create a contact and search an existing organization', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('Luke');
    cy.get('[data-test-id="last-name"]').type('Skywalker');
    cy.get('[data-test-id="email"]').type('luke.skywalker@jedicorp.com');
    //search for an existing organization
    cy.get('#search-organization-input').type('jedicorp');
    //select the organization from the dropdown
    cy.get('[data-test-id="orga-to-select"]')
      .find('span')
      .contains('jedicorp')
      .click();
    //add job title
    cy.get('[data-test-id="job"]').type('Jedi Knight');
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should('contain', 'Luke Skywalker');
  });

  it('can create a contact and create a new organization with an existing group and no departments', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('baby');
    cy.get('[data-test-id="last-name"]').type('yoda');
    cy.get('[data-test-id="email"]').type('baby.yoda@jedicorp.com');
    //search for a non existing organization
    cy.get('#search-organization-input').type('master jedi corp');
    //click on create organization button
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    //select yes for national group
    cy.get('#natGroup-yes').click({ force: true });
    //search for an existing group
    cy.get('[data-test-id="search-group-input"]').type('Jedicorp');
    //select the group from the dropdown
    cy.get('[data-test-id="orga-group-to-select"]')
      .find('span')
      .contains('Jedicorp')
      .click();
    //create the organization
    cy.get('[data-test-id="button-create-new-organization"]').click();
    //add job title
    cy.get('[data-test-id="job"]').type('Jedi Master');
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should('contain', 'baby yoda');
  });

  it('can create a contact and create a new organization and create a group and select departments', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('darth');
    cy.get('[data-test-id="last-name"]').type('vader');
    cy.get('[data-test-id="email"]').type('darth.vader@sithcorp.com');
    cy.get('[data-test-id="job"]').type('Jedi Master');
    //search for a non existing organization
    cy.get('#search-organization-input').type('sithcorp2');
    //click on create organization button
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    //select a department
    cy.get('#select-list-input').click();
    cy.get('[data-test-id="select-list-options"]')
      .find('div')
      .contains('(93) Département de test numéro 3')
      .click();
    //select yes for national group
    cy.get('#natGroup-yes').click({ force: true });
    //search for a non existing group
    cy.get('[data-test-id="search-group-input"]').type('imsupersad', {
      delay: 0,
    });
    //create the group from the dropdown
    cy.get('[data-test-id="button-create-organization-group"]').click({
      force: true,
    });
    cy.wait(300);
    //select the group from the dropdown
    cy.get('[data-test-id="orga-group-to-select"]')
      .find('span')
      .contains('imsupersad')
      .click();
    //create the organization
    cy.get('[data-test-id="button-create-new-organization"]').click({
      force: true,
    });
    cy.wait(1000);
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should('contain', 'darth vader');
  });

  it('can create a contact and create a new organization with an existing group and one department', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('obiwan');
    cy.get('[data-test-id="last-name"]').type('kenobi');
    cy.get('[data-test-id="email"]').type('obiwan.kenobi@jedicorp.com');
    //search for a non existing organization
    cy.get('#search-organization-input').type(
      'between master and knight jedi corp'
    );
    //click on create organization button
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    //select a department
    cy.get('#select-list-input').click();
    cy.get('[data-test-id="select-list-options"]')
      .find('div')
      .contains('(93) Département de test numéro 3')
      .click();
    //select yes for national group
    cy.get('#natGroup-yes').click({ force: true });
    //search for an existing group
    cy.get('[data-test-id="search-group-input"]').type('Jedicorp');
    //select the group from the dropdown
    cy.get('[data-test-id="orga-group-to-select"]')
      .find('span')
      .contains('Jedicorp')
      .click();
    //create the organization
    cy.get('[data-test-id="button-create-new-organization"]').click();
    //add job title
    cy.get('[data-test-id="job"]').type('Jedi Master');
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should('contain', 'obiwan kenobi');
  });

  it('can create a contact and create a new organization and create a group and no department', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('han');
    cy.get('[data-test-id="last-name"]').type('solo');
    cy.get('[data-test-id="email"]').type('han.solo@sithcorp.com');
    cy.get('[data-test-id="job"]').type('thief');
    //search for a non existing organization
    cy.get('#search-organization-input').type('thiefcorp');
    //click on create organization button
    cy.get('[data-test-id="button-create-organization"]').click({
      force: true,
    });
    //select yes for national group
    cy.get('#natGroup-yes').click({ force: true });
    //search for a non existing group
    cy.get('[data-test-id="search-group-input"]').type('imgood');
    //create the group from the dropdown
    cy.get('[data-test-id="button-create-organization-group"]').click();
    cy.wait(300);
    //select the group from the dropdown
    cy.get('[data-test-id="orga-group-to-select"]')
      .find('span')
      .contains('imgood')
      .click();
    //create the organization
    cy.get('[data-test-id="button-create-new-organization"]').click({
      force: true,
    });
    cy.wait(1000); //wait for the organization to be created before submitting the contact form
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]').should('contain', 'han solo');
  });

  it('can edit an existing organization on contactbook', () => {
    cy.visit(`/addressbook/contacts`);
    cy.wait(1000); //wait for the page to load
    // wait until headers exist
    cy.get('[data-test-id="organization-header"] h3.organization__name', { timeout: 10000 })
    .should('have.length.greaterThan', 0);

    // find the one h3 that includes "Jedicorp" and click its edit button
    cy.get('[data-test-id="organization-header"] h3.organization__name', { timeout: 10000 })
      .filter((_, el) => el.textContent.replace(/\s+/g, ' ').trim().toLowerCase().includes('jedicorp'))
      .first()
      .should('exist')
      .scrollIntoView()
      .should('be.visible')
      .closest('[data-test-id="organization-header"]')
      .within(() => {
        cy.get('[data-test-id="button-edit-organization"]')
          .should('exist')
          .click({ force: true });
      });
    //change the name of the organization
    cy.get('[data-test-id="organization-name"]')
      .clear()
      .type('Jedicorp edited');
    //submit the organization form
    cy.get('[data-test-id="button-create-new-organization"]').click({
      force: true,
    });
    //reload page to see the organization
    cy.reload();
    //verify that the organization is created
    cy.get('[data-test-id="organization-header"]').should(
      'contain',
      'Jedicorp edited'
    );
  });

  it('can edit an existing contact on contactbook', () => {
    cy.visit(`/addressbook/contacts`);
    //click on edit card contact
    cy.contains('[data-test-id="contact-card"]', 'Anakin Skywalker')
      .should('be.visible')
      .closest('[data-test-id="contact-card"]')
      .within(() => {
        cy.get('[data-test-id="button-edit-contact"]').click({ force: true });
      });
    // Edit the job title
    cy.get('[data-test-id="job"]').clear().type('Sith Lord');
    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'Anakin Skywalker')
      .should('contain', 'Sith Lord');
  });
});
