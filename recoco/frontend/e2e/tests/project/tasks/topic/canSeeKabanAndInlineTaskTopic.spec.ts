import { expect, test } from '../../../../fixtures';
import { becomeAdvisor, createProject, createTask } from '../../../../helpers/commands';
import { authFile } from '../../../../helpers/users';

let currentProjectId: string;

// TODO Réécrire : kanban/list-tasks-switch-button et task-kanban-topic n'existent plus
test.describe.skip(
  'I can go to tasks tab',
  { tag: '@page-projet-recommandations' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeEach(async ({ page }) => {
      currentProjectId = await createProject(page, 'test project 2');
    });

    test('sees a task kanban topic', async ({ page }) => {
      await page.goto(`/project/${currentProjectId}`);
      await becomeAdvisor(page, currentProjectId); // A remplacer par une fixture avec un user déjà advisor du dossier
      await page.goto(`/project/${currentProjectId}/actions`);

      await createTask(page, 'inline task', 'kanban topic');

      await page
        .locator('[data-test-id="kanban-tasks-switch-button"]')
        .click({ force: true });
      await expect(
        page.locator('[data-test-id="kanban-tasks-switch-button"]')
      ).toBeChecked();
      await expect(
        page.locator('[data-test-id="task-kanban-topic"]')
      ).toBeAttached();
      await page
        .locator('[data-test-id="list-tasks-switch-button"]')
        .click({ force: true });
      await expect(
        page.locator('[data-test-id="task-inline-topic"]')
      ).toBeAttached();
    });
  }
);

// page recommandation
