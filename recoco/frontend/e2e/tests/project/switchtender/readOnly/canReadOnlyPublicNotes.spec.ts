import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';

test.describe(
  'I cannot access conversation without join project',
  { tag: '@page-projet-conversations' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('cant goes to public notes ', async ({ page }) => {
      await page.goto(`/project/29/`);

      await expect(
        page.locator('[data-test-id="project-navigation-conversations-new"]')
      ).toHaveAttribute('disabled');
    });
  }
);
