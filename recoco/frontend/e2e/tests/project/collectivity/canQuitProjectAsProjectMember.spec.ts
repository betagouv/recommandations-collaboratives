import projects from '../../../../cypress/fixtures/projects/projects.json';
import { test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

const currentProject = projects[17];

test.describe(
  'As collectivity project member, I can quit a project if I am not the owner',
  { tag: '@page-projet-parametres-quitter-projet' },
  () => {
    test.use({ storageState: authFile('collectivité2') });

    test('I can quit a project from the project preferences', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}/administration/`);
      const projectView = new ProjectView(page);
      await projectView.quitProject('member');
    });
  }
);
