import path from 'node:path';

import { expect, test } from '@playwright/test';

import file from '../../../../cypress/fixtures/documents/file.json';
import projects from '../../../../cypress/fixtures/projects/projects.json';
import { Editor } from '../../../helpers/tools/editor';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.use({ storageState: authFile('conseiller1') });

test.describe(
  'I can add a file with my message in public notes',
  { tag: '@page-projet-conversations-nouveau-message' },
  () => {
    test('writes a message with a file', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/conversations`);

      const editor = new Editor(page);
      const now = new Date();

      const textarea = page.locator('textarea');
      await textarea.fill(`test avec fichier : ${now}`);
      await expect(textarea).toHaveValue(`test avec fichier : ${now}`);

      await editor.writeMessage(`test avec fichier : ${now}`);

      await page
        .locator('[name="the_file"]')
        .setInputFiles(path.resolve(__dirname, '../../../../', file.path));

      await page.getByText('Envoyer').click({ force: true });

      await expect(
        page.getByText(`test avec fichier : ${now}`).first()
      ).toBeVisible();
      await expect(
        page.getByText(file.path.slice(-17, -4)).first()
      ).toBeVisible();
    });
  }
);
