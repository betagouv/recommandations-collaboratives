import { expect, test } from '../../fixtures';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can access the Dashboard Page with a non UI login',
  { tag: '@connexion' },
  () => {
    test('should access the dashboard', async ({ page }) => {
      const response = await page.goto('/');
      expect(response?.ok()).toBeTruthy();
    });
  }
);
