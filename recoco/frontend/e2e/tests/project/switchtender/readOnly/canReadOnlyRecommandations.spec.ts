import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

// TODO Réécrire pour la nouvelle interface conversation (/actions redirige vers /conversations#actions)
test.describe.skip(
  'I can read only recommandations',
  { tag: '@page-projet-recommandations' },
  () => {
    test.use({ storageState: authFile('conseiller2') });

    test('goes to recommandations and read only content', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/actions`);

      await expect(page.getByText('Ajouter une recommandation')).toHaveCount(0);
    });
  }
);

// page recommandations
