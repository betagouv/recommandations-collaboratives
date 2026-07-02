import projects from '../../../../cypress/fixtures/projects/projects.json';
import { test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

const ownerEmail = 'bob@test.fr';

test.describe(
  'As project owner, I can see project email reminders',
  { tag: '@page-projet-presentation-rappel-email' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('Displays no reminder message on projects with no scheduled emails', async ({
      page,
    }) => {
      const currentProject = projects[19];
      await page.goto(`/project/${currentProject.pk}`);
      const projectView = new ProjectView(page);
      await projectView.checkNextEmailReminder({});
    });

    test('Displays a reminder message when an email is scheduled to be sent', async ({
      page,
    }) => {
      const currentProject = projects[20];
      await page.goto(`/project/${currentProject.pk}`);
      const projectView = new ProjectView(page);
      await projectView.checkNextEmailReminder({ email: ownerEmail });
    });

    test('Reminders settings popup is accessible and provides access to preferences panel', async ({
      page,
    }) => {
      const currentProject = projects[20];
      await page.goto(`/project/${currentProject.pk}`);
      const projectView = new ProjectView(page);
      await projectView.openEmailReminderTooltip(true, ownerEmail);
    });
  }
);
