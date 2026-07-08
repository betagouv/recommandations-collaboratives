import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[2];

test.describe(
  'I can have a public url to share',
  { tag: '@page-projet-edl-partager' },
  () => {
    test.use({ storageState: authFile('collectivité2') });

    test('goes to share a project page', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/connaissance`);

      await page
        .locator('[data-test-id="public-share-button"]')
        .click({ force: true });

      // await expect(page).toHaveURL(/\/access\//)

      const value = await page.locator('[x-ref="input"]').inputValue();
      await page.goto(value);
      await expect(page).toHaveURL(/\/project\/partage\//);
    });
  }
);
