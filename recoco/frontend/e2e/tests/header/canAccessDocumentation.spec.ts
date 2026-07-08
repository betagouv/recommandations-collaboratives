import { expect, test } from '../../fixtures';

test.describe(
  'I can access documentation',
  { tag: '@acces-rapide-utilisateur' },
  () => {
    test('displays as staff member', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto('/');
      await page
        .locator("[data-test-id='open-dropdown-profil-option-button']")
        .click({ force: true });
      const url = await page
        .locator('[data-test-id="documentation-button-staff"]')
        .getAttribute('href');
      const response = await page.request.get(url!);
      expect(response.status()).toBe(200);
    });

    test('displays as advisor', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto('/');
      await page
        .locator("[data-test-id='open-dropdown-profil-option-button']")
        .click({ force: true });
      const url = await page
        .locator('[data-test-id="documentation-button-advisor"]')
        .getAttribute('href');
      const response = await page.request.get(url!);
      expect(response.status()).toBe(200);
    });

    test('cannnot displays it', async ({ loginAs }) => {
      const page = await loginAs('collectivité1');
      await page.goto('/');
      await page
        .locator('[data-test-id="open-dropdown-profil-option-button"]')
        .click({ force: true });
      await expect(page.getByText('Documentation')).toHaveCount(0);
    });
  }
);
