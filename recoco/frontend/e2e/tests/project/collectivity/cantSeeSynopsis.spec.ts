import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[3];

test.describe(
  "I can access overview page and can't see the synopsis",
  { tag: '@page-projet-presentation-resume-saisine' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test("goes to overview page and can't see synopsis", async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await expect(page.getByText('Reformulation du besoin')).toHaveCount(0);
    });
  }
);
