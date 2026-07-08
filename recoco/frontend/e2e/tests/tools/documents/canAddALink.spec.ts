import { expect, test } from '@playwright/test';

import link from '../../../../cypress/fixtures/documents/link.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('collectivité1') });

test.describe(
  'I can add a link on the document tab',
  { tag: '@page-projet-fichier-epingler-lien' },
  () => {
    test('add a link', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await page.evaluate(() => {
        const popover = document.getElementById('link-popover');
        if (popover) {
          popover.setAttribute('style', 'display:block !important;');
        }
      });

      const theLink = page.locator('[name="the_link"]');
      await theLink.fill(link.url);
      await expect(theLink).toHaveValue(link.url);
      const description = page.locator('#link-description');
      await description.fill(link.description);
      await expect(description).toHaveValue(link.description);
      await page.locator('#link-submit-button').click({ force: true });
    });

    test('show the link in the link list', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/documents`);

      await expect(page.getByText(link.description).first()).toBeVisible();
    });
  }
);
