import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access knowledge tab in a project as a member',
  { tag: '@navigation-projet @page-projet-edl' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to the knowledge page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='project-navigation-knowledge']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/connaissance'));
    });
  }
);

test.describe(
  'I can access knowledge tab in a project as an advisor',
  { tag: '@navigation-projet @page-projet-edl' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to the knowledge page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='project-navigation-knowledge']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/connaissance'));
    });
  }
);
