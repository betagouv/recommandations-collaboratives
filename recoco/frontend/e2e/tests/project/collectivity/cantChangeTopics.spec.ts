import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  "I can't change topics of a project",
  { tag: '@page-projet-presentation-thematique' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to overview page and should not see edit topic button', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await expect(page).toHaveURL(/\/presentation/);

      await expect(page.getByText('Identifier les sujets')).toHaveCount(0);
    });
  }
);
