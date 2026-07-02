import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  "I can't access privates notes as a non positionned adviser",
  { tag: '@page-projet-espace-conseiller' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('goes to the project page and not beeing able to see the private note tab', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await expect(page.getByText('Suivi interne')).toHaveCount(0);
    });
  }
);
