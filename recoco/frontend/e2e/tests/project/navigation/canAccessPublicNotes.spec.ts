import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access public notes tab in a project as a member',
  { tag: '@navigation-projet @page-projet-conversations' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to the public note page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page.getByText('Conversation').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/conversations'));
    });
  }
);

test.describe(
  'I can access public notes tab in a project as an advisor',
  { tag: '@navigation-projet @page-projet-conversations' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to the public note page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page.getByText('Conversation').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/conversations'));
    });
  }
);
