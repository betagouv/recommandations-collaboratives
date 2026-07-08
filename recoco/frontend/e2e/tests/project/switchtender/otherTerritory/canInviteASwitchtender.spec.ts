import { test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can invite a switchtender as a regional actor',
  { tag: '@page-projet-presentation-inviter-suivie' },
  () => {
    test.use({ storageState: authFile('conseiller3') });

    test('goes to the overview page and invite a switchtender', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
    });
  }
);
