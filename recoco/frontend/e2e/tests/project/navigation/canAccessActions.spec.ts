import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

// TODO Réécrire pour la nouvelle interface conversation+panneau actions
//      (l'onglet "Recommandations" n'existe plus, /actions redirige vers /conversations#actions)
test.describe.skip(
  'I can access actions tab in a project as a member',
  { tag: '@navigation-projet @page-projet-recommandations' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to the action page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page.getByText('Recommandations').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/actions'));
    });
  }
);

test.describe.skip(
  'I can access actions tab in a project as an advisor',
  { tag: '@navigation-projet @page-projet-recommandations' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to the action page of my project', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page.getByText('Recommandations').click({ force: true });
      await expect(page).toHaveURL(new RegExp('/actions'));
    });
  }
);

// page dossier
