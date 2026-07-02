import { expect, test } from '../../../fixtures';

test.describe(
  'I can see CTA on survey page',
  { tag: '@page-projet-edl-completer' },
  () => {
    test('should display CTA as collectivity', async ({ loginAs }) => {
      const page = await loginAs('collectivité1');
      await page.goto(`/project/2/connaissance`);
      await expect(
        page.locator('[data-test-id="link-fill-survey-cta"]').first()
      ).toBeVisible();
    });

    test('should not display CTA as staff', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/2/connaissance`);
      await expect(
        page.locator('[data-test-id="link-fill-survey-cta"]')
      ).toHaveCount(0);
    });

    // Titre dédoublonné : le 2e « should not display CTA as staff » Cypress teste le rôle conseiller
    test('should not display CTA as advisor', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/2/connaissance`);
      await expect(
        page.locator('[data-test-id="link-fill-survey-cta"]')
      ).toHaveCount(0);
    });
  }
);
