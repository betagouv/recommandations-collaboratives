import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../helpers/users';

const currentProject = projects[2];
const message = 'Message - Test comment on task';

test.use({ storageState: authFile('conseiller1') });

// TODO Réécrire : edit-comment-button et list-tasks-switch-button n'existent plus
test.describe.skip(
  'As advisor, I can make a comment on a task',
  { tag: '@page-projet-recommandations-modification' },
  () => {
    test('adds a new comment, and stops from submitting the comment more than once', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}/actions`);

      await expect(
        page.locator('[data-test-id="list-tasks-switch-button"]')
      ).toBeChecked();
      await expect(
        page.locator('[data-test-id="task-initial-comment"]').first()
      ).toBeAttached();

      await page
        .locator('[data-test-id="edit-comment-button"]')
        .first()
        .click({ force: true });

      await page
        .locator('[data-test-id="tiptap-editor-content"] .ProseMirror')
        .click();
      await page.keyboard.type(message);

      await page
        .locator('[data-test-id="button-submit-new"]')
        .click({ force: true });
      await expect(
        page.locator('[data-test-id="task-initial-comment"]')
      ).toContainText(message);
    });
  }
);
