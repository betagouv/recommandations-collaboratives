import { expect, test } from '@playwright/test';

import contacts from '../../../../cypress/fixtures/addressbook/contacts.json';
import { authFile } from '../../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can assign new contacts when I edit a resource',
  { tag: '@acces-ressources' },
  () => {
    test('goes to edit a resource suppress and assign 3 new contacts', async ({
      page,
    }) => {
      await page.goto('/ressource/1/');
      await page.locator('[data-test-id="edit-resource"]').click();

      const deleteButtons = page.locator(
        '[data-test-id="button-delete-contact"]'
      );
      // cy.get().each() attendait l'existence avant d'itérer (délai élargi :
      // la liste des contacts se charge lentement quand le serveur est chargé)
      await expect(deleteButtons.first()).toBeAttached({ timeout: 20_000 });
      const deleteCount = await deleteButtons.count();
      for (let i = 0; i < deleteCount; i++) {
        await deleteButtons.first().click({ force: true });
      }

      const searchContact = page.locator('#search-contact-input');
      await searchContact.pressSequentially('lala');
      await expect(searchContact).toHaveValue('lala');
      await page
        .locator('[data-test-id="contact-card-component"]')
        .first()
        .click({ force: true });
      await page
        .locator('[data-test-id="button-add-contact-to-tiptap-editor"]')
        .click({ force: true });

      await searchContact.pressSequentially('lili');
      await expect(searchContact).toHaveValue('lili');
      await page
        .locator('[data-test-id="contact-card-component"]')
        .filter({ hasText: 'lili' })
        .first()
        .click({ force: true });
      await page
        .locator('[data-test-id="button-add-contact-to-tiptap-editor"]')
        .click({ force: true });

      await searchContact.pressSequentially('lulu');
      await expect(searchContact).toHaveValue('lulu');
      await page
        .locator('[data-test-id="contact-card-component"]')
        .filter({ hasText: 'lulu' })
        .first()
        .click({ force: true });
      await page
        .locator('[data-test-id="button-add-contact-to-tiptap-editor"]')
        .click({ force: true });

      await page
        .locator('[data-test-id="publish-resource-btn"]')
        .click({ force: true });

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(
        page.getByText(contacts[1].fields.first_name as string).first()
      ).toBeVisible();
      await expect(
        page.getByText(contacts[2].fields.first_name as string).first()
      ).toBeVisible();
      await expect(
        page.getByText(contacts[3].fields.first_name as string).first()
      ).toBeVisible();
    });
  }
);
