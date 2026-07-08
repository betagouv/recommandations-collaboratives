import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to overview tab and check invitation project member button',
  { tag: '@page-projet-presentation-inviter-partenaire' },
  () => {
    test.use({ storageState: authFile('national') });

    test('shows disabled button to invite new project member', async ({
      page,
    }) => {
      await page.goto('/project/1/presentation');
      await expect(
        page.locator('[data-cy="invite-project-member-button"]')
      ).toBeDisabled();
    });
  }
);
