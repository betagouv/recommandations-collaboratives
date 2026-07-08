import { expect, test } from '@playwright/test';

import documents from '../../../../cypress/fixtures/documents/documents.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can delete a file on the document tab',
  { tag: '@page-projet-fichier-supprimer' },
  () => {
    test('deletes a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await page
        .getByText(documents[3].fields.description)
        .first()
        .locator('xpath=../../..')
        .locator('#file-delete-button')
        .click({ force: true });

      await expect(
        page.getByText('Le document a bien été supprimé').first()
      ).toBeVisible();
    });

    test('must not show the deleted link', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await expect(
        page.getByText(documents[3].fields.description)
      ).toHaveCount(0);
    });
  }
);
