import { test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { Editor } from '../../../helpers/tools/editor';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('conseiller1') });

test.describe(
  "I can't send an empty message",
  { tag: '@page-projet-conversations-nouveau-message' },
  () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/conversations`);
    });

    test('enables and disables the send message if I erase my message (empty message)', async ({
      page,
    }) => {
      const editor = new Editor(page);

      await editor.checkSubmitButton(true);

      await page.waitForTimeout(500);

      await editor.writeMessage(`new message`);

      await editor.checkSubmitButton(false);

      await editor.clear();

      await editor.checkSubmitButton(true);
    });
  }
);
