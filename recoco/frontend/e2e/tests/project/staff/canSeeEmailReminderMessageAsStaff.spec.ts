import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { ProjectView } from '../../../helpers/views/project';
import { authFile } from '../../../helpers/users';

const ownerEmail = 'bob@test.fr';

test.describe(
  'As staff, I can see project email reminders',
  { tag: '@page-projet-presentation-rappel-email' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('Displays no reminder message on projects with no scheduled emails', async ({
      page,
    }) => {
      const currentProject = projects[19];
      await page.goto(`/project/${currentProject.pk}`);
      const projectView = new ProjectView(page);
      await projectView.checkNextEmailReminder({ role: 'staff' });
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
      await projectView.checkEmailReminderTooltip(false);
    });
  }
);
