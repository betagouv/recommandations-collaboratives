import path from 'node:path';

import { expect, test } from '@playwright/test';

import file from '../../../../cypress/fixtures/documents/file.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can add a file on the document tab',
  { tag: '@page-projet-fichier-ajouter' },
  () => {
    test('upload a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await page.evaluate(() => {
        const popover = document.getElementById('popover');
        if (popover) {
          popover.setAttribute('style', 'display:block !important;');
        }
      });

      await page
        .locator('[name="the_file"]')
        .setInputFiles(path.resolve(__dirname, '../../../../', file.path));
      const description = page.locator('#document-description');
      await description.fill(file.description);
      await expect(description).toHaveValue(file.description);
      await page.locator('#document-submit-button').click({ force: true });

      await expect(
        page.getByText('Le document a bien été enregistré').first()
      ).toBeVisible();
    });

    test('show the file in the file list', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await expect(page.getByText(file.description).first()).toBeVisible();
    });
  }
);
