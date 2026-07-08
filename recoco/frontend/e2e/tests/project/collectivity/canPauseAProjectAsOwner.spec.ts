import projects from '../../../../cypress/fixtures/projects/projects.json';
import { test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

const currentProject = projects[17];

test.describe(
  'As project owner, I can pause a project',
  { tag: '@page-projet-parametres-pause-projet' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
    });

    test('Pauses a project from the project preferences', async ({ page }) => {
      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      await projectView.deactivateProject();
    });

    test('Reactivates a project from the project preferences', async ({
      page,
    }) => {
      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      await projectView.activateProjectFromPreferences();
    });
  }
);
