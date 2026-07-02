import path from 'node:path';

import { expect, test } from '@playwright/test';

import file from '../../../../cypress/fixtures/documents/file.json';
import { becomeAdvisor, createProject } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

let currentProjectId: string;

test.use({ storageState: authFile('conseiller1') });

// TODO Réécrire : la création de tâche redirige désormais vers /conversations
test.describe.skip(
  'I can add a file in a task',
  { tag: '@page-projet-recommandations-modal' },
  () => {
    test.beforeEach(async ({ page }) => {
      currentProjectId = await createProject(page, 'file in task');
    });

    test('writes a message with a file', async ({ page }) => {
      await page.goto(`/project/${currentProjectId}`);

      await becomeAdvisor(page, currentProjectId);
      await page.goto(`/project/${currentProjectId}/actions`);

      await page
        .locator("[data-test-id='submit-task-button']")
        .click({ force: true });

      await page.locator('#push-noresource').click({ force: true });

      const now = new Date();

      const intent = page.locator('#intent');
      await intent.fill('fake recommandation with no resource');
      await expect(intent).toHaveValue('fake recommandation with no resource');

      await page.locator('.ProseMirror p').first().click();
      await page.keyboard.type(
        `fake recommandation content with no resource : ${now}`
      );

      await page
        .locator('[name="the_file"]')
        .setInputFiles(path.resolve(__dirname, '../../../../', file.path));

      await page.locator('[type=submit]').click({ force: true });

      await expect(page).toHaveURL(/\/actions/);

      await expect(
        page.getByText('fake recommandation content with no resource').first()
      ).toBeVisible();
    });
  }
);
