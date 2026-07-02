import { expect, test } from '@playwright/test';

import contacts from '../../../../cypress/fixtures/addressbook/contacts.json';
import { authFile } from '../../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can assign some contacts when I create a resource',
  { tag: '@acces-ressources' },
  () => {
    test('goes to create a resource and assign 3 contacts', async ({ page }) => {
      await page.goto('/ressource/create/');

      const title = page.locator('#id_title');
      await title.fill('Ressource de test');
      await expect(title).toHaveValue('Ressource de test');

      const subtitle = page.locator('#id_subtitle');
      await subtitle.fill('Soustitre de la ressource de test');
      await expect(subtitle).toHaveValue('Soustitre de la ressource de test');

      const summary = page.locator('#id_summary');
      await summary.fill('résumé de la ressource de test');
      await expect(summary).toHaveValue('résumé de la ressource de test');

      const tags = page.locator('#id_tags');
      await tags.fill('etiquette1');
      await expect(tags).toHaveValue('etiquette1');

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

      await page.waitForTimeout(500);

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

      const expiresOn = page.locator('#id_expires_on');
      await expiresOn.fill('2022-12-20');
      await expect(expiresOn).toHaveValue('2022-12-20');

      await page.locator('.ProseMirror p').first().click();
      await page.keyboard.type('text');

      await page
        .locator('[data-test-id="publish-resource-btn"]')
        .click({ force: true });

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(page.getByText('Ressource de test').first()).toBeVisible();
      await expect(
        page.getByText('résumé de la ressource de test').first()
      ).toBeVisible();

      await expect(
        page.getByText(contacts[1].fields.first_name as string).first()
      ).toBeVisible();
      await expect(
        page.getByText(contacts[2].fields.first_name as string).first()
      ).toBeVisible();
    });
  }
);
