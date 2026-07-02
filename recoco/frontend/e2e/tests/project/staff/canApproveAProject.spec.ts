import { expect, test } from '@playwright/test';

import { authFile } from '../../../helpers/users';

test.describe(
  'I can go to the dashboard and see the pending projects, and approve one',
  { tag: '@acces-moderation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('approves a project', async ({ page }) => {
      await page.goto('/projects/moderation');
      await page
        .locator("[data-test-id='project-card']", { hasText: 'Friche numéro 4' })
        .locator('[data-test-id="accept-project"]')
        .getByText('Accepter')
        .first() // cy.contains prenait le 1er bouton (« Accepter », pas « Accepter et rejoindre »)
        .click({ force: true });

      await expect(page).toHaveURL(new RegExp('/project/'));
      await expect(page.getByText('Friche numéro 4').first()).toBeVisible();

      await page.goto('/projects/moderation');
      await expect(
        page.locator('[data-test-id="moderation-page"]')
      ).not.toContainText('Friche numéro 4');
    });
  }
);
