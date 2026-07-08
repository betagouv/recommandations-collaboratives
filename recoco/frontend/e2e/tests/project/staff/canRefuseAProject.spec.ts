import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to the dashboard and see the pending projects, and refuse one',
  { tag: '@acces-moderation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('refuses a project', async ({ page }) => {
      await page.goto('/projects/moderation');

      await page
        .locator("[data-test-id='project-card']", { hasText: 'Friche à refuser' })
        .locator('[data-test-id="refuse-project"]')
        .getByText('Refuser')
        .click();

      await expect(page).toHaveURL(new RegExp('/projects/moderation/'));

      await expect(
        page.locator('[data-test-id="moderation-page"]')
      ).not.toContainText('Friche à refuser');
    });
  }
);
