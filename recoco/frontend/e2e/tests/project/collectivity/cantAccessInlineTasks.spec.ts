import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

// TODO Réécrire : page /actions redirige et tasks-inline-button n'existe plus
test.describe.skip(
  "I can go to action page but can't see the loop to access the inline tasks",
  { tag: '@page-projet-recommandations' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test("goes to action page and can't see inline tasks loop button", async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}/actions`);

      await expect(page.locator('#tasks-inline-button')).toHaveCount(0);
    });
  }
);

// page recommandations
