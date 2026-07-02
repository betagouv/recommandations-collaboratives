import { expect, test } from '../../../fixtures';
import { becomeAdvisor, createProject, createTask } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

let currentProjectId: string;
// TODO Réécrire : #unpublish-task-button et list-tasks-switch-button n'existent plus
test.describe.skip(
  'I can go tasks tab',
  {
    tag: [
      '@page-projet-recommandations',
      '@page-projet-recommandations-brouillon',
    ],
  },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeEach(async ({ page }) => {
      currentProjectId = await createProject(page, 'unpublish task');
    });

    test('unpublishes a task', async ({ page }) => {
      await becomeAdvisor(page, currentProjectId); // A remplacer par une fixture avec un user déjà advisor du projet

      await page.goto(`/project/${currentProjectId}/actions`);

      await createTask(page, 'unpublish task');

      await expect(
        page.locator('[data-test-id="list-tasks-switch-button"]')
      ).toBeChecked();

      await page.locator('#unpublish-task-button').click({ force: true });

      await expect(page.getByText('brouillon').first()).toBeVisible();
    });
  }
);

// page recommandations
