import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access overview tab in a project as a member',
  { tag: '@navigation-projet @page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to knowledge page and then overview page of my project', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='project-navigation-knowledge']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/connaissance'));
      await page.getByText('Présentation').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/presentation'));
    });
  }
);

test.describe(
  'I can access overview tab in a project as an advisor',
  { tag: '@navigation-projet @page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to knowledge page and then overview page of my project', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='project-navigation-knowledge']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/connaissance'));
      await page.getByText('Présentation').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/presentation'));
    });
  }
);
