import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can see an expired resource as a switchtender',
  { tag: '@acces-ressources' },
  () => {
    test('sees an expired resource', async ({ page }) => {
      await page.goto('/ressource/3/');

      await expect(
        page.locator("[data-test-id='expired-resource-banner']").first()
      ).toBeAttached();
    });
  }
);
