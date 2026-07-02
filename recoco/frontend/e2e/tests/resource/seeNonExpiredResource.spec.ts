import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can see a non expired resource as a switchtender',
  { tag: '@acces-ressources' },
  () => {
    test('sees a non expired resource', async ({ page }) => {
      await page.goto('/ressource/2/');

      await expect(
        page.locator("[data-test-id='non-expired-resource-banner']").first()
      ).toBeAttached();
    });
  }
);
