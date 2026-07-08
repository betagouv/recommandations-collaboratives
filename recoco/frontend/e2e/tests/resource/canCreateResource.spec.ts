import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can create a resource as a switchtender',
  { tag: '@acces-ressources' },
  () => {
    test('creates a resource', async ({ page }) => {
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

      const expiresOn = page.locator('#id_expires_on');
      await expiresOn.fill('2022-12-20');
      await expect(expiresOn).toHaveValue('2022-12-20');

      await page.locator('.ProseMirror p').first().click();
      await page.keyboard.type('text');

      // await page.locator('[data-cy="button-ressource-create"]').click({ force: true });
      await page
        .locator('[data-cy="form-resource-create"]')
        .evaluate((form) => (form as HTMLFormElement).requestSubmit());

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(page.getByText('Ressource de test').first()).toBeVisible();
      await expect(
        page.getByText('résumé de la ressource de test').first()
      ).toBeVisible();
    });
  }
);
