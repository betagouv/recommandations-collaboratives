import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[3];

test.describe(
  'I can access and use public notes',
  { tag: '@page-projet-espace-conseiller' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to public notes', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await expect(page.getByText('Suivi interne')).toHaveCount(0);
    });
  }
);
