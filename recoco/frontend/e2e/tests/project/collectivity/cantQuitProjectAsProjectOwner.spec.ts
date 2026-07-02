import projects from '../../../../cypress/fixtures/projects/projects.json';
import { test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

const currentProject = projects[17];

test.describe(
  'As project owner, I cannot quit a project',
  { tag: '@page-projet-parametres-quitter-projet' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}`);
    });

    test(`I can't quit a project that I own`, async ({ page }) => {
      const projectView = new ProjectView(page);
      await projectView.navigateToPreferencesTab();
      // 'owner' n'est pas dans l'union de types de quitProject ; il tombe dans
      // la branche default, strictement identique à un appel sans argument.
      await projectView.quitProject();
    });
  }
);
