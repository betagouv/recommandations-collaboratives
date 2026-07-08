import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can read only project state',
  { tag: '@page-projet-edl' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('goes to project state and read only content', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await page
        .locator('[data-test-id="project-navigation-knowledge"]')
        .click();

      await expect(page).toHaveURL(/\/connaissance/);

      await expect(page.getByText('Compléter cette section')).toHaveCount(0);
    });
  }
);
