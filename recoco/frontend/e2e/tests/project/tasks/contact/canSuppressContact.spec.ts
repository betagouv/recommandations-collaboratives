import { expect, test } from '../../../../fixtures';

test.describe.skip(
  'I can suppress a contact from the contactbook',
  { tag: '@page-projet-recommandations-modification' },
  () => {
    test('can suppress a contact from the contactbook as staff', async ({
      loginAs,
    }) => {
      const page = await loginAs('staff');
      await page.goto(`/addressbook/contacts/`);
      const card = page
        .locator('[data-test-id="contact-card"]')
        .filter({ hasText: 'à supprimer' });

      await card
        .locator('[data-test-id="button-delete-contact"]')
        .click({ force: true });
      await card.locator('.modal__footer-confirm').click({ force: true });

      await expect(
        page
          .locator('[data-test-id="contact-card"]')
          .filter({ hasText: 'à supprimer' })
      ).toHaveCount(0);
    });
  }
);
