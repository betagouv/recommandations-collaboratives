import projects from '../../../../cypress/fixtures/projects/projects.json';
import { test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

const currentProject = projects[21];

test.describe.configure({ mode: 'serial' });

test.describe(
  `As non referent project member, I can see a project's active status`,
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('collectivité2') });

    test.beforeAll(async ({ browser }) => {
      // First: login as owner and deactivate project
      const context = await browser.newContext({
        storageState: authFile('collectivité1'),
      });
      const page = await context.newPage();
      await page.goto(`/project/${currentProject.pk}/administration`);
      const projectView = new ProjectView(page);
      await projectView.deactivateProject();
      await context.close();
    });

    test('Displays a header banner when a project is paused', async ({
      page,
    }) => {
      // Then: login as non referent project member and check banner
      await page.goto(`/project/${currentProject.pk}/administration`);
      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      await projectView.checkProjectStatusBanner(true);
    });
  }
);
