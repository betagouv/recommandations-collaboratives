import { expect, test } from '../../../../fixtures';
import { ProjectView } from '../../../../helpers/views/project';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[17];

test.describe.configure({ mode: 'serial' });

test.describe(
  `As project advisor, I can see a project's active status`,
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeAll(async ({ browser }) => {
      // First: login as owner and deactivate project
      const context = await browser.newContext({
        storageState: authFile('staff'), // TODO replace by staffOnSite and check behaviour
      });
      const page = await context.newPage();
      await page.goto(`/project/${currentProject.pk}`);

      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      await projectView.deactivateProject();
      await context.close();
    });

    test('Displays a header banner when a project is paused', async ({
      page,
    }) => {
      // Then: login as non referent project member and check banner
      await page.goto(`/project/${currentProject.pk}`);
      await new ProjectView(page).checkProjectStatusBanner(true);
    });
  }
);
