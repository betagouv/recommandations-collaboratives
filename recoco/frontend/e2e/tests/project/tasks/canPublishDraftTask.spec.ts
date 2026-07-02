import { expect, test } from '../../../fixtures';
import { becomeAdvisor, createProject, logout } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

let currentProjectId: string;
// TODO Réécrire pour la nouvelle interface conversation
//      (les boutons publish/unpublish/update étaient dans task_actions.html supprimé)
test.describe.skip(
  'I can go to tasks tab',
  {
    tag: [
      '@page-projet-recommandations',
      '@page-projet-recommandations-creation',
    ],
  },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeEach(async ({ page }) => {
      currentProjectId = await createProject(page, 'draft project');
      await logout(page);
    });

    test('publishes a task', async ({ loginAs }) => {
      const page = await loginAs('conseiller2');
      await page.goto(`/project/${currentProjectId}/actions`);
      await becomeAdvisor(page, currentProjectId);
      await page.goto(`/project/${currentProjectId}/actions`);

      await page.locator('[data-test-id="submit-task-button"]').click();
      await expect(
        page.locator('[data-cy="reco-pusher-selected-project"]')
      ).toContainText('draft project');
      await page.locator('#push-noresource').click({ force: true });

      const intent = page.locator('#intent');
      await intent.fill('draft project');
      await expect(intent).toHaveValue('draft project');

      const description = page.locator('textarea');
      await description.fill('reco test from action description');
      await expect(description).toHaveValue('reco test from action description');

      await page.locator('.ProseMirror p').click();
      await page.keyboard.type('reco test for draft task');

      await page
        .locator('[data-test-id="publish-draft-task-button"]')
        .click();

      await expect(page).toHaveURL(/\/actions/);

      await expect(page.getByText('draft project').first()).toBeVisible();

      await expect(
        page.locator('[data-test-id="list-tasks-switch-button"]')
      ).toBeChecked();

      await page.locator('#unpublish-task-button').click({ force: true });
      await expect(
        page.locator('[data-test-id="task-draft-status"]')
      ).toBeVisible();
      await page.locator('#publish-task-button').click({ force: true });
      await expect(
        page.locator('[data-test-id="task-draft-status"]')
      ).toHaveCount(0);
      await page
        .locator('[data-test-id="update-task-action-button"]')
        .click({ force: true });
      await page
        .locator('textarea')
        .fill('reco test from action description modification');
      await page.locator('[data-cy="button-submit-task"]').click();
      await expect(page).toHaveURL(/\/actions/);
      await expect(
        page.getByText('reco test from action description modification').first()
      ).toBeVisible();
    });
  }
);

// page recommandations
