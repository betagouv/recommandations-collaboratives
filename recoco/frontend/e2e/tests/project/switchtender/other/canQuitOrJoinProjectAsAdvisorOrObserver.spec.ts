import { expect, test } from '../../../../fixtures';
import { ProjectView } from '../../../../helpers/views/project';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[17];

test.describe(
  'As an advisor, I can quit a project',
  { tag: '@page-projet-parametres-quitter-projet' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
    });

    test('I can quit or join a project as observer or advisor', async ({
      page,
    }) => {
      const projectView = new ProjectView(page);
      await projectView.joinAsAdvisorWithSelector();
      await expect(
        page.locator('[data-test-id="button-quit-role"]').first()
      ).toBeAttached();
      await projectView.quitProjectRole();
    });
  }
);
