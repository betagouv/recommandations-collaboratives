import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.describe(
  'I can access to my address book',
  { tag: '@acces-rapide-utilisateur' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('', async ({ page }) => {
      await page.goto('/');
      await page
        .locator("[data-test-id='open-dropdown-profil-option-button']")
        .click({ force: true });
      // L'entrée du dropdown est hors viewport : équivalent du force:true Cypress
      await page
        .locator("[data-test-id='button-address-book']")
        .dispatchEvent('click');
      await expect(page).toHaveURL(/\/addressbook\/contacts/);
    });
  }
);

test.describe(
  "I can't see adress book because I don't have one",
  { tag: '@acces-rapide-utilisateur' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('', async ({ page }) => {
      await page.goto('/');
      await page
        .locator('[data-test-id="open-dropdown-profil-option-button"]')
        .click({ force: true });
      await expect(
        page.locator('[data-test-id="button-address-book"]').first()
      ).toBeAttached();
    });
  }
);
