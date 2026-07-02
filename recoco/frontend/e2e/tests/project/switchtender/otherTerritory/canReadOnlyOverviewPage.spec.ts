import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';

test.describe(
  'I can read only overview page',
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('goes to the overview page and not see the advisor note', async ({
      page,
    }) => {
      await page.goto(`/project/29`);

      await expect(page.getByText('Note interne')).toHaveCount(0);
    });
  }
);
