import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can access to 403 page when cannot access to the page',
  { tag: '@error-page' },
  () => {
    test('should show relogin url on custom 403 page when authenticated', async ({
      page,
    }) => {
      await page.goto('/project/10/presentation');
      await expect(
        page.locator('[data-test-id="technicat-info"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-test-id="link-relogin-403"]')
      ).toBeVisible();
    });
  }
);
