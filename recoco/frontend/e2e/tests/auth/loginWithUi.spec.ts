import users from '../../../cypress/fixtures/users/users.json';
import { expect, test } from '../../fixtures';

test.describe('The Login Page', { tag: '@connexion' }, () => {
  let currentUser: (typeof users)[number]['fields'];

  test.beforeEach(() => {
    currentUser = users[1].fields;
  });

  test('sets auth cookie when logging in via form submission', async ({
    page,
  }) => {
    const { username } = currentUser;

    await page.goto('/accounts/login/');

    await expect(page).toHaveURL(/\/accounts\/login\//);

    const loginInput = page.locator('#id_login');
    await loginInput.fill(username);
    await expect(loginInput).toHaveValue(username);

    const passwordInput = page.locator('#id_password');
    await passwordInput.fill('Recoco2000');
    await expect(passwordInput).toHaveValue('Recoco2000');

    await page.locator('[type=submit]').click({ force: true });

    await expect(
      page.getByText(`Connexion avec ${username} réussie.`)
    ).toBeVisible();

    // we should be redirected to /dashboard
    await expect(page).toHaveURL(/\/projects/);

    // our auth cookie should be present
    const cookies = await page.context().cookies();
    expect(cookies.find((cookie) => cookie.name === 'sessionid')).toBeTruthy();
  });
});
