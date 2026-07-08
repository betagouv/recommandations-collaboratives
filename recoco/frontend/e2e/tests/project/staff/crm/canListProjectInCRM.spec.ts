import { expect, test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../../helpers/users';

const projectCommune3Length = projects.filter(
  (project) => project.fields.commune === 3
).length;

test.describe(
  'I can go to CRM and list projects',
  { tag: '@bouton-raccourci-crm-staff' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test.beforeEach(async ({ page }) => {
      await page.goto(`/crm/project`);
    });

    test.skip('lists projects', async ({ page }) => {
      await expect(page.getByText(projects[0].fields.name).first()).toBeVisible();
      await expect(page.getByText('random name')).toHaveCount(0);
      await expect(
        page.locator('[data-test-id="projects-count-label"]')
      ).toContainText(
        `${projects.length} résultat${projects.length > 1 ? 's' : ''}`
      );
    });

    test.skip('filters projects by name', async ({ page }) => {
      await page
        .locator('[data-cy="search-bar-project"]')
        .pressSequentially(projects[projects.length - 1].fields.name);
      await expect(
        page.getByText(projects[projects.length - 1].fields.name).first()
      ).toBeVisible();
      await expect(
        page.locator('[data-test-id="projects-count-label"]')
      ).toContainText(`1 résultat`);
      const searchBar = page.locator('[data-cy="search-bar-project"]');
      await searchBar.fill('');
      await searchBar.pressSequentially('random name with no results');
      await expect(page.getByText('Aucun résultat').first()).toBeVisible();
      await expect(
        page.locator('[data-test-id="projects-count-label"]')
      ).toContainText(`Aucun résultat`);
    });

    test.skip('filters projects department', async ({ page }) => {
      await page.locator('#allTerritory').uncheck({ force: true });
      await page.waitForTimeout(300);
      await page.locator('#93').check({ force: true });
      await expect(
        page
          .getByText(
            projects.find((project) => project.fields.commune === 3)!.fields.name
          )
          .first()
      ).toBeVisible();
      await expect(
        page.locator('[data-test-id="projects-count-label"]')
      ).toContainText(`${projectCommune3Length} résultats`);
    });
  }
);
