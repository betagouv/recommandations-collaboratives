import { expect, test } from '../../../../fixtures';
import { shareContact, typeInTiptapEditor } from '../../../../helpers/commands';
import { authFile } from '../../../../helpers/users';

test.describe.skip(
  'I can search and share a contact on a message editor',
  { tag: '@page-projet-recommandations-modification' },
  () => {
    test.use({ storageState: authFile('staff') });

    // TODO Réécrire : task-item et la preview modal ont été supprimés
    test.skip('can search, select and share a contact on a followup', async ({
      page,
    }) => {
      await page.goto(`/project/2/actions#`);
      //click on recommandation
      await page
        .locator('[data-test-id="task-item"]')
        .first()
        .click({ force: true });

      //fonction to search and attach a contact
      await shareContact(page, 'Lala');

      //validate message followup
      await page
        .locator('[data-test-id="button-submit-new"]')
        .click({ force: true });
      //my contact should be visible on the followup
      await expect(
        page.locator('[data-test-id="contact-card"]').first()
      ).toBeVisible();
    });

    test('can search, select and share a contact on a conversation', async ({
      page,
    }) => {
      await page.goto(`/project/2/conversations`);

      //fonction to search and attach a contact
      await shareContact(page, 'Lala');

      //write a message
      await typeInTiptapEditor(page, 'Here is my contact');

      //validate message on conversation
      await page
        .locator('[data-test-id="send-message-conversation"]')
        .click({ force: true });
      //my contact should be visible on the conversation
      await expect(
        page.locator('[data-test-id="contact-card"]').first()
      ).toBeVisible();
    });

    test('can search, select and share a contact on advisor space', async ({
      page,
    }) => {
      await page.goto(`/project/2/suivi`);

      //fonction to search and attach a contact
      await shareContact(page, 'Lala');

      //write a message
      await typeInTiptapEditor(page, 'Here is my contact');

      //validate message on advisor space
      await page
        .locator('[data-test-id="submit-message-button-on-advisor-space"]')
        .click({ force: true });

      //my contact should be visible on the advisor space
      await expect(
        page.locator('[data-test-id="contact-card"]').first()
      ).toBeVisible();
    });

    // TODO Réécrire : create-task-button n'est plus accessible depuis /actions (page redirigée)
    test.skip('can create a contact, an organization and a national group and share the contact on a new task', async ({
      page,
    }) => {
      await page.goto(`/project/2/actions#`);
      //click on create recommandation
      await page
        .locator('[data-test-id="create-task-button"]')
        .click({ force: true });

      //create a recommandation without resource
      await page
        .locator('[data-cy="radio-push-reco-no-resource"]')
        .click({ force: true });
      //write resource title
      await page.locator('[data-cy="input-title-task"]').fill('Test contact');
      //write a message
      await typeInTiptapEditor(page, 'Here is my contact');
      //click on add contact button
      await page
        .locator('[data-test-id="button-add-contact-in-editor"]')
        .click({ force: true });
      //create a contact
      await page
        .locator('[data-test-id="button-create-contact"]')
        .click({ force: true });
      //search an non existing organization
      await page
        .locator('#search-organization-input')
        .pressSequentially('Test organization');
      //create an organization
      await page
        .locator('[data-test-id="button-create-organization"]')
        .click({ force: true });
      await page.locator('#natGroup-yes').click({ force: true });
      await page
        .locator('[data-test-id="search-group-input"]')
        .pressSequentially('Test group');
      //create a national group
      await page
        .locator('[data-test-id="button-create-organization-group"]')
        .click({ force: true });
      // create organization
      await page
        .locator('[data-test-id="button-create-new-organization"]')
        .click({ force: true });
      //create contact
      await page.locator('[data-test-id="last-name"]').fill('Test');
      await page.locator('[data-test-id="first-name"]').fill('Contact');
      await page.locator('[data-test-id="job"]').fill('testeur');
      await page.locator('[data-test-id="email"]').fill('test@test.test');
      await page.locator('[data-test-id="phone"]').fill('0123456789');
      await page
        .locator('[data-test-id="create-contact-button"]')
        .click({ force: true });
      await page
        .locator('[data-test-id="button-add-contact-to-tiptap-editor"]')
        .click({ force: true });

      //save resource as draft
      await page
        .locator('[data-test-id="publish-draft-task-button"]')
        .click({ force: true });

      //my contact should be visible on the followup
      await expect(
        page.locator('[data-test-id="contact-card"]').first()
      ).toBeVisible();
    });
  }
);
