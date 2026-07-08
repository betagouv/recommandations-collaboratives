import { expect, test } from '@playwright/test';

import documents from '../../../../cypress/fixtures/documents/documents.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can bookmark and unbookmark a file',
  { tag: '@page-projet-fichier-favori' },
  () => {
    test('boomark a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await page
        .getByText(documents[2].fields.description)
        .first()
        .locator('xpath=../../..')
        .locator('#file-is-not-bookmarked')
        .click();
      await expect(
        page
          .getByText(documents[2].fields.description)
          .first()
          .locator('xpath=../../..')
          .locator('#file-is-bookmarked')
      ).toBeAttached();
    });

    test('unboomark a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await page
        .getByText(documents[1].fields.description)
        .first()
        .locator('xpath=../../..')
        .locator('#file-is-bookmarked')
        .click();

      await expect(
        page
          .getByText(documents[1].fields.description)
          .first()
          .locator('xpath=../../..')
          .locator('#file-is-not-bookmarked')
      ).toBeAttached();
    });
  }
);
