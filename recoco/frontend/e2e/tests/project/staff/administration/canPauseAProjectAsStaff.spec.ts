import { test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import { ProjectView } from '../../../../helpers/views/project';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[19];

test.describe.configure({ mode: 'serial' });

test.describe(
  'As site staffOnSite, I can pause and reactivate a project',
  { tag: '@page-projet-parametres-pause-projet' },
  () => {
    test.use({ storageState: authFile('staffOnSite') });

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
