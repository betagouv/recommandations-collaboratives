import { test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can see a draft resource as a switchtender',
  { tag: '@acces-ressources' },
  () => {
    test('sees a draft resource', async ({ page }) => {
      await page.goto('/ressource/3/');
    });
  }
);
