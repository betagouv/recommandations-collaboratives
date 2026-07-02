import { expect, test } from '@playwright/test';

import { authFile } from '../../../../helpers/users';

test.describe(
  'I can go to the dashboard and search for project',
  { tag: '@recherche-kanban-projets' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test.beforeEach(async ({ page }) => {
      await page.goto('/projects');
    });

    test('search project by name', async ({ page }) => {
      await expect(page.locator('[data-cy="loader"]')).toBeHidden();
      const cards = page.locator('[data-cy="card-project"]');
      // cy.get attendait l'existence des cartes avant de compter
      await expect(cards.first()).toBeVisible();
      const projectsLength = await cards.count();
      expect(projectsLength).toBeGreaterThan(0);
      await page
        .locator('[data-cy="search-bar-project"]')
        .pressSequentially('map area commune');
      await expect
        .poll(async () => await cards.count())
        .toBeLessThan(projectsLength);
      await expect(page.getByText('Map Area Commune').first()).toBeVisible();
    });

    test('does not display pre-draft projects on kanban', async ({ page }) => {
      await expect(page.locator('[data-cy="loader"]')).toBeHidden();
      const cards = page.locator('[data-cy="card-project"]');
      // cy.get attendait l'existence des cartes avant de compter
      await expect(cards.first()).toBeVisible();
      const projectsLength = await cards.count();
      expect(projectsLength).toBeGreaterThan(0);
      await page
        .locator('[data-cy="search-bar-project"]')
        .pressSequentially('pre-draft');
      await expect(page.getByText('Dossier pre-draft')).toHaveCount(0);
    });

    test('could not display unknown project', async ({ page }) => {
      await expect(page.locator('[data-cy="loader"]')).toBeHidden();
      const cards = page.locator('[data-cy="card-project"]');
      // cy.get attendait l'existence des cartes avant de compter
      await expect(cards.first()).toBeVisible();
      const projectsLength = await cards.count();
      expect(projectsLength).toBeGreaterThan(0);
      await page
        .locator('[data-cy="search-bar-project"]')
        .pressSequentially("n'importe qoi");
      await expect(page.locator('[data-cy="card-project"]')).toHaveCount(0);
    });

    test('could search by territory', async ({ page }) => {
      await expect(page.locator('[data-cy="loader"]')).toBeHidden();
      const cards = page.locator('[data-cy="card-project"]');
      // cy.get attendait l'existence des cartes avant de compter
      await expect(cards.first()).toBeVisible();
      const projectsLength = await cards.count();
      expect(projectsLength).toBeGreaterThan(0);

      await page.locator('[data-cy="check-display-project"]').click();
      await expect(page.locator('#region-1')).toBeVisible();
      await expect(page.locator('#region-1')).toBeChecked();
      await page.locator('#region-1').uncheck();
      await expect(page.getByText('93170')).toHaveCount(0);
    });
  }
);
