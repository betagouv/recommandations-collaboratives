import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to a project and see if the main collaborator has accepted the invitation',
  { tag: '@changement-role-projet' },
  () => {
    test.use({ storageState: authFile('jean') });

    test('can see if the main colloborator has accepted the invitation or not', async ({
      page,
    }) => {
      await page.goto('/project/27/presentation');
      await expect(
        page.locator('[data-test-id="invite-not-accepted-banner"]').first()
      ).toBeAttached();

      await page.goto('/project/23/presentation');
      await expect(
        page.locator('[data-test-id="invite-not-accepted-banner"]')
      ).toHaveCount(0);
    });
  }
);
