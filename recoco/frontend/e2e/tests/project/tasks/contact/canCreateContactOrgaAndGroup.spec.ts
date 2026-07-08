import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';

test.describe.skip(
  'I can create and edit a contact and an organization on contactbook',
  { tag: '@page-projet-recommandations-creation' },
  () => {
    test.use({ storageState: authFile('staff') });

    test('can create a contact and create a new organization with no group and no departments', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('Anakin');
      await page.locator('[data-test-id="last-name"]').fill('Skywalker');
      await page
        .locator('[data-test-id="email"]')
        .fill('anakin.skywalker@jedicorp.com');
      //search for a non existing organization
      await page.locator('#search-organization-input').pressSequentially('jedicorp');
      //click on create organization button
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      //create the organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click();
      //add job title
      await page.locator('[data-test-id="job"]').fill('Jedi Knight');
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'Anakin Skywalker' })
          .first()
      ).toBeVisible();
    });

    test('can create a contact and search an existing organization', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('Luke');
      await page.locator('[data-test-id="last-name"]').fill('Skywalker');
      await page
        .locator('[data-test-id="email"]')
        .fill('luke.skywalker@jedicorp.com');
      //search for an existing organization
      await page.locator('#search-organization-input').pressSequentially('jedicorp');
      //select the organization from the dropdown
      await page
        .locator('[data-test-id="orga-to-select"]')
        .locator('span')
        .filter({ hasText: 'jedicorp' })
        .first()
        .click();
      //add job title
      await page.locator('[data-test-id="job"]').fill('Jedi Knight');
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'Luke Skywalker' })
          .first()
      ).toBeVisible();
    });

    test('can create a contact and create a new organization with an existing group and no departments', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('baby');
      await page.locator('[data-test-id="last-name"]').fill('yoda');
      await page
        .locator('[data-test-id="email"]')
        .fill('baby.yoda@jedicorp.com');
      //search for a non existing organization
      await page
        .locator('#search-organization-input')
        .pressSequentially('master jedi corp');
      //click on create organization button
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      //select yes for national group
      await page.locator('#natGroup-yes').click({ force: true });
      //search for an existing group
      await page
        .locator('[data-test-id="search-group-input"]')
        .pressSequentially('Jedicorp');
      //select the group from the dropdown
      await page
        .locator('[data-test-id="orga-group-to-select"]')
        .locator('span')
        .filter({ hasText: 'Jedicorp' })
        .first()
        .click();
      //create the organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click();
      //add job title
      await page.locator('[data-test-id="job"]').fill('Jedi Master');
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'baby yoda' })
          .first()
      ).toBeVisible();
    });

    test('can create a contact and create a new organization and create a group and select departments', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('darth');
      await page.locator('[data-test-id="last-name"]').fill('vader');
      await page
        .locator('[data-test-id="email"]')
        .fill('darth.vader@sithcorp.com');
      await page.locator('[data-test-id="job"]').fill('Jedi Master');
      //search for a non existing organization
      await page
        .locator('#search-organization-input')
        .pressSequentially('sithcorp2');
      //click on create organization button
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      //select a department
      await page.locator('#select-list-input').click();
      await page
        .locator('[data-test-id="select-list-options"]')
        .locator('div')
        .filter({ hasText: '(93) Département de test numéro 3' })
        .first()
        .click();
      //select yes for national group
      await page.locator('#natGroup-yes').click({ force: true });
      //search for a non existing group
      await page
        .locator('[data-test-id="search-group-input"]')
        .pressSequentially('imsupersad');
      //create the group from the dropdown
      await page
        .locator('[data-test-id="button-create-organization-group"]')
        .click({ force: true });
      await page.waitForTimeout(300);
      //select the group from the dropdown
      await page
        .locator('[data-test-id="orga-group-to-select"]')
        .locator('span')
        .filter({ hasText: 'imsupersad' })
        .first()
        .click();
      //create the organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click({ force: true });
      await page.waitForTimeout(1000);
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'darth vader' })
          .first()
      ).toBeVisible();
    });

    test('can create a contact and create a new organization with an existing group and one department', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('obiwan');
      await page.locator('[data-test-id="last-name"]').fill('kenobi');
      await page
        .locator('[data-test-id="email"]')
        .fill('obiwan.kenobi@jedicorp.com');
      //search for a non existing organization
      await page
        .locator('#search-organization-input')
        .pressSequentially('between master and knight jedi corp');
      //click on create organization button
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      //select a department
      await page.locator('#select-list-input').click();
      await page
        .locator('[data-test-id="select-list-options"]')
        .locator('div')
        .filter({ hasText: '(93) Département de test numéro 3' })
        .first()
        .click();
      //select yes for national group
      await page.locator('#natGroup-yes').click({ force: true });
      //search for an existing group
      await page
        .locator('[data-test-id="search-group-input"]')
        .pressSequentially('Jedicorp');
      //select the group from the dropdown
      await page
        .locator('[data-test-id="orga-group-to-select"]')
        .locator('span')
        .filter({ hasText: 'Jedicorp' })
        .first()
        .click();
      //create the organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click();
      //add job title
      await page.locator('[data-test-id="job"]').fill('Jedi Master');
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'obiwan kenobi' })
          .first()
      ).toBeVisible();
    });

    test('can create a contact and create a new organization and create a group and no department', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      //click on create contact button
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //fill in the contact form
      await page.locator('[data-test-id="first-name"]').fill('han');
      await page.locator('[data-test-id="last-name"]').fill('solo');
      await page
        .locator('[data-test-id="email"]')
        .fill('han.solo@sithcorp.com');
      await page.locator('[data-test-id="job"]').fill('thief');
      //search for a non existing organization
      await page
        .locator('#search-organization-input')
        .pressSequentially('thiefcorp');
      //click on create organization button
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      //select yes for national group
      await page.locator('#natGroup-yes').click({ force: true });
      //search for a non existing group
      await page
        .locator('[data-test-id="search-group-input"]')
        .pressSequentially('imgood');
      //create the group from the dropdown
      await page
        .locator('[data-test-id="button-create-organization-group"]')
        .click();
      await page.waitForTimeout(300);
      //select the group from the dropdown
      await page
        .locator('[data-test-id="orga-group-to-select"]')
        .locator('span')
        .filter({ hasText: 'imgood' })
        .first()
        .click();
      //create the organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click({ force: true });
      await page.waitForTimeout(1000); //wait for the organization to be created before submitting the contact form
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'han solo' })
          .first()
      ).toBeVisible();
    });

    test('can edit an existing organization on contactbook', async ({
      page,
    }) => {
      await page.goto(`/addressbook/contacts`);
      await page.waitForTimeout(1000); //wait for the page to load
      // wait until headers exist
      await expect
        .poll(
          () =>
            page
              .locator(
                '[data-test-id="organization-header"] h3.organization__name'
              )
              .count(),
          { timeout: 10000 }
        )
        .toBeGreaterThan(0);

      // find the one h3 that includes "Jedicorp" and click its edit button
      const orgHeader = page
        .locator('[data-test-id="organization-header"]')
        .filter({
          has: page.locator('h3.organization__name', { hasText: /jedicorp/i }),
        })
        .first();
      await orgHeader.scrollIntoViewIfNeeded();
      await expect(orgHeader).toBeVisible();
      await orgHeader
        .locator('[data-test-id="button-edit-organization"]')
        .click({ force: true });
      //change the name of the organization
      const organizationName = page.locator(
        '[data-test-id="organization-name"]'
      );
      await organizationName.clear();
      await organizationName.fill('Jedicorp edited');
      //submit the organization form
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click({ force: true });
      //reload page to see the organization
      await page.reload();
      //verify that the organization is created
      await expect(
        page
          .locator('[data-test-id="organization-header"]')
          .filter({ hasText: 'Jedicorp edited' })
          .first()
      ).toBeVisible();
    });

    test('can edit an existing contact on contactbook', async ({ page }) => {
      await page.goto(`/addressbook/contacts`);
      //click on edit card contact
      const card = page
        .locator('[data-test-id="contact-card"]')
        .filter({ hasText: 'Anakin Skywalker' })
        .first();
      await expect(card).toBeVisible();
      await card
        .locator('[data-test-id="button-edit-contact"]')
        .click({ force: true });
      // Edit the job title
      const job = page.locator('[data-test-id="job"]');
      await job.clear();
      await job.fill('Sith Lord');
      //submit the contact form
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      //reload page to see the contact
      await page.reload();
      //verify that the contact is created
      const editedCard = page
        .locator('[data-test-id="contact-card"]')
        .filter({ hasText: 'Anakin Skywalker' })
        .first();
      await expect(editedCard).toContainText('Anakin Skywalker');
      await expect(editedCard).toContainText('Sith Lord');
    });
  }
);
