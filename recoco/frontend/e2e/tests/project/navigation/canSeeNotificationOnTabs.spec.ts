import path from 'node:path';

import { expect, test } from '@playwright/test';

import file from '../../../../cypress/fixtures/documents/file.json';
import { createTask, typeInTiptapEditor } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

const currentProjectId = 25;

test.describe.configure({ mode: 'serial' });

test.describe(
  'I can access tabs and see notifications',
  { tag: '@navigation-projet' },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test.beforeAll(async ({ browser }) => {
      // collectivité1 : aucun badge de notification au départ
      const memberContext = await browser.newContext({
        storageState: authFile('collectivité1'),
      });
      const memberPage = await memberContext.newPage();
      await memberPage.goto(`/project/${currentProjectId}/presentation`);
      await expect(
        memberPage.locator('[data-test-id="badge-tab-new-task"]')
      ).toHaveCount(0);
      await expect(
        memberPage.locator('[data-test-id="badge-tab-new-message"]')
      ).toHaveCount(0);
      await expect(
        memberPage.locator('[data-test-id="badge-tab-new-file"]')
      ).toHaveCount(0);
      await memberContext.close();

      // conseiller1 : crée une tâche, un message et un fichier pour générer des notifications
      const advisorContext = await browser.newContext({
        storageState: authFile('conseiller1'),
      });
      const advisorPage = await advisorContext.newPage();

      // Create a task to have a notification
      await advisorPage.goto(`/project/${currentProjectId}/actions`);
      await createTask(advisorPage, 'Tâche notification');

      // Create message to have a notification
      await advisorPage.goto(`/project/${currentProjectId}/conversations`);
      const now = new Date();

      const textarea = advisorPage.locator('textarea').first();
      await textarea.fill(`test : ${now}`);
      await expect(textarea).toHaveValue(`test : ${now}`);

      await typeInTiptapEditor(advisorPage, `test : ${now}`);
      await advisorPage.getByText('Envoyer').click({ force: true });
      await expect(
        advisorPage.locator('[data-test-id="send-message-conversation"]')
      ).toBeDisabled();
      await expect(advisorPage.getByText(`test : ${now}`).first()).toBeVisible();

      // Post a file to have a notification
      await advisorPage.goto(`/project/${currentProjectId}/documents`);

      await advisorPage.evaluate(() => {
        const popover = document.getElementById('popover');
        if (popover) {
          popover.setAttribute('style', 'display:block !important;');
        }
      });

      await advisorPage
        .locator('[name="the_file"]')
        .setInputFiles(path.resolve(__dirname, '../../../../', file.path));
      const description = advisorPage.locator('#document-description');
      await description.fill(file.description);
      await expect(description).toHaveValue(file.description);
      await advisorPage
        .locator('#document-submit-button')
        .click({ force: true });

      await expect(
        advisorPage.getByText('Le document a bien été enregistré').first()
      ).toBeVisible();
      await advisorContext.close();
    });

    test('goes to the action page of my project', async ({ page }) => {
      await page.goto(`/project/25/presentation`);
      await expect(
        page.locator('[data-test-id="badge-tab-new-message"]').first()
      ).toBeAttached();
    });
  }
);
