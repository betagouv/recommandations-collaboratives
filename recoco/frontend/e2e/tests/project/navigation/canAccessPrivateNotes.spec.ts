import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access private notes tab in a project as a switchtender',
  { tag: '@navigation-projet @page-projet-espace-conseiller' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to the private notes page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page.getByText('Espace conseillers').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/suivi'));
    });
  }
);
