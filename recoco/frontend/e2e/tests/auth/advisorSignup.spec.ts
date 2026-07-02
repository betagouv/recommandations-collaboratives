import { expect, test } from '../../fixtures';
import { checkCaptcha } from '../../helpers/commands';

test.describe('Signup advisor', { tag: '@demande-compte-conseiller' }, () => {
  const userToSignup: Record<string, string> = {
    '[name=first_name]': 'Signupuser',
    '[name=last_name]': 'Successful',
    '[name=organization]': 'Signup Corp',
    '[name=organization_position]': 'Tester',
    '[name=email]': 'signupuuhu@success.test',
    '[name=phone_no]': '0102030405',
    '[name=password1]': 'Recoco2000',
    '[name=password2]': 'Recoco2000',
  };

  test('signup a new advisor', async ({ page }) => {
    await page.goto('/acteurs-locaux');
    await page
      .locator('[data-test-id="button-advisor-access-request"]')
      .click();

    await expect(page).toHaveURL(/\/advisor-access-request/);

    for (const [selector, value] of Object.entries(userToSignup)) {
      await page.locator(selector).fill(value);
    }

    await checkCaptcha(page, 500);
    await page.locator('[type=submit]').click();

    await expect(page).toHaveURL(/\/advisor-access-request/);
    await page
      .locator('[data-test-id="advisor-access-type-national"]')
      .check({ force: true });

    await page.locator('[name="comment"]').fill("Tester c'est douter");
    await page.locator('[type=submit]').click();

    await expect(
      page.locator('[data-test-id="pending-advisor-request-confirmation"]')
    ).toBeVisible();
  });
});
