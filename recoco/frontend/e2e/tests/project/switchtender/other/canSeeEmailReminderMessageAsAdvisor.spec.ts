import { test } from '../../../../fixtures';
import { ProjectView } from '../../../../helpers/views/project';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const ownerEmail = 'bob@test.fr';

test.describe(
  'As project advisor, I can see project email reminders',
  { tag: '@page-projet-presentation-rappel-email' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('Displays no reminder message on projects with no scheduled emails', async ({
      page,
    }) => {
      const currentProject = projects.find((x) => x.pk == 20)!;
      await page.goto(`/project/${currentProject.pk}`);
      await new ProjectView(page).checkNextEmailReminder({ role: 'advisor' });
    });

    test('Displays a reminder message when an email is scheduled to be sent', async ({
      page,
    }) => {
      const currentProject = projects.find((x) => x.pk == 21)!;
      await page.goto(`/project/${currentProject.pk}`);
      await new ProjectView(page).checkNextEmailReminder({ email: ownerEmail });
    });

    test('Reminders settings popup is accessible and provides access to preferences panel', async ({
      page,
    }) => {
      const currentProject = projects.find((x) => x.pk == 21)!;
      await page.goto(`/project/${currentProject.pk}`);
      await new ProjectView(page).checkEmailReminderTooltip();
    });
  }
);
