import { expect, test } from '@playwright/test';

import { authFile } from '../../../../helpers/users';

//TODO: Verify when the fixing frontend test environment is done
test.describe(
  'I can go to the dashboard and see only my projects',
  { tag: '@page-kanban-projets' },
  () => {
    test.use({ storageState: authFile('jean') });

    test.beforeEach(async ({ page }) => {
      await page.goto('/projects/staff/');
    });

    test('search project by name', async ({ page }) => {
      // Playwright ignore le clipping/masquage par un ancêtre ; on filtre les
      // cartes réellement visibles (équivalent du display !== 'none' Cypress).
      const visibleCards = page.locator('[data-cy="card-project"]:visible');
      // cy.get attendait l'existence des cartes avant de compter
      await expect(visibleCards.first()).toBeVisible();
      const projectsLength = await visibleCards.count();

      const toggle = page.locator('[data-test-id="my-projects-toggle"]');
      await expect(toggle).not.toBeChecked();
      await toggle.check();
      await expect
        .poll(async () => await visibleCards.count())
        .toBeLessThan(projectsLength);
    });
  }
);
