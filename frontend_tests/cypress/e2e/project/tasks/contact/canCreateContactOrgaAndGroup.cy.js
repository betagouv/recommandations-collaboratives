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
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'Anakin Skywalker');
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
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'Luke Skywalker');
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
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'baby yoda');
  });

  it('can create a contact and create a new organization and create a group and select departments', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('darth');
    cy.get('[data-test-id="last-name"]').type('vader');
    cy.get('[data-test-id="email"]').type('darth.vader@sithcorp.com');
    //search for a non existing organization
    cy.get('#search-organization-input').type('sithcorp');
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
    cy.get('[data-test-id="search-group-input"]').type('imsupersad');
    //create the group from the dropdown
    cy.get('[data-test-id="button-create-organization-group"]').click();
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

    cy.get('[data-test-id="job"]').type('Jedi Master');

    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'darth vader');
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
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'obiwan kenobi');
  });

  it('can create a contact and create a new organization and create a group and no department', () => {
    cy.visit(`/addressbook/contacts`);
    //click on create contact button
    cy.get('[data-test-id="button-create-contact"]').click({ force: true });
    //fill in the contact form
    cy.get('[data-test-id="first-name"]').type('han');
    cy.get('[data-test-id="last-name"]').type('solo');
    cy.get('[data-test-id="email"]').type('han.solo@sithcorp.com');
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

    cy.get('[data-test-id="job"]').type('thief');

    //submit the contact form
    cy.get('[data-test-id="create-contact-button"]').click({ force: true });
    //reload page to see the contact
    cy.reload();
    //verify that the contact is created
    cy.get('[data-test-id="contact-card"]')
      .should('contain', 'han solo');
  });

  xit('can edit an existing contact on contactbook', () => {
    cy.visit(`/addressbook/contacts`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //search for a contact
    cy.get('#search-contact-input').type('Test', { force: true });
    //select a contact
    cy.get('[data-test-id="contact-to-select"]').first().click({ force: true });
    //send contact to tiptap editor
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });
    //validate message followup
    cy.get('[data-test-id="button-submit-new"]').click({ force: true });
    //my contact should be visible on the followup
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });

  xit('can edit an existing organization on contactbook', () => {
    cy.visit(`/project/2/actions#`);
    //click on recommandation
    cy.get('[data-test-id="task-item"]').first().click({ force: true });
    //click on add contact button
    cy.get('[data-test-id="button-add-contact"]').click({ force: true });
    //search for a contact
    cy.get('#search-contact-input').type('Test', { force: true });
    //select a contact
    cy.get('[data-test-id="contact-to-select"]').first().click({ force: true });
    //send contact to tiptap editor
    cy.get('[data-test-id="button-add-contact-to-tiptap-editor"]').click({
      force: true,
    });
    //validate message followup
    cy.get('[data-test-id="button-submit-new"]').click({ force: true });
    //my contact should be visible on the followup
    cy.get('[data-test-id="contact-card"]').should('be.visible');
  });
});
