import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can access and use public notes',
  { tag: '@page-projet-conversations' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('clicks on the "public note" button', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await page.getByText('Conversation').first().click({ force: true });

      await expect(page).toHaveURL(/\/conversations/);
    });
  }
);
