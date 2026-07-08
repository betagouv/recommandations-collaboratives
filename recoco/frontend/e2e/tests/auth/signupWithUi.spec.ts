import project from '../../../cypress/fixtures/projects/project.json';
import { expect, test } from '../../fixtures';
import { createProject } from '../../helpers/commands';

test.describe('The Signup Page', { tag: '@inscription' }, () => {
  const userToSignup: Record<string, string> = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=org_name]': 'Signup Corp',
    '[name=role]': 'Tester',
    '[name=email]': 'signup4@success.test',
    '[name=phone]': '0102030405',
    '[name=password]': 'Recoco2000',
  };

  test('signup a new user', async ({ page }) => {
    await createProject(page, 'Test signup', project, true, userToSignup);
  });

  test('cannot signup without creating a projet', async ({ page }) => {
    await page.goto('/accounts/signup/');
    await expect(page.locator('form')).toHaveCount(0);
  });
});
