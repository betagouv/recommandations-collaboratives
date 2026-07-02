import { test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import { ProjectView } from '../../../../helpers/views/project';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[17];

test.describe(
  'As site staff, I can quit a project',
  { tag: '@page-projet-parametres-quitter-projet' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
      const projectView = new ProjectView(page);
      await projectView.joinAsAdvisorWithSelector();
    });

    test('I can quit a project from the project preferences', async ({
      page,
    }) => {
      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      await projectView.quitProject('staff');
    });
  }
);
