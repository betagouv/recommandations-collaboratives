import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';

test.describe(
  'I can read only overview page',
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('goes to overview and read only content', async ({ page }) => {
      await page.goto(`/project/29`);

      await expect(page).toHaveURL(/\/presentation/);

      await expect(
        page.getByText('Note interne aux conseillers')
      ).toHaveCount(0);
    });
  }
);
