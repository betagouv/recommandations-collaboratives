import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[2];

test.describe(
  "I can't change topics of a project I don't advise",
  { tag: '@page-projet-presentation-thematique' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to overview page and should not see edit topic button', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await expect(page).toHaveURL(/\/presentation/);

      await expect(page.getByText('Identifier les sujets')).toHaveCount(0);
    });
  }
);
