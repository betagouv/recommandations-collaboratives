import { expect, test } from '../../../../fixtures';
import { becomeAdvisor, createProject, createTask } from '../../../../helpers/commands';
import { authFile } from '../../../../helpers/users';
import resources from '../../../../../cypress/fixtures/resources/resources.json';

const currentResource = resources[4];
const taskName = 'task intent';
let currentProjectId: string;

// TODO Réécrire : list-tasks-switch-button n'existe plus, /actions redirige vers /conversations
test.describe.skip(
  'I can go to tasks tab',
  {
    tag: ['@page-projet-recommandations', '@page-projet-recommandations-modal'],
  },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test.beforeEach(async ({ page }) => {
      currentProjectId = await createProject(page, 'new task');
    });

    test('creates a task with a resource and see the initial comment', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProjectId}`);
      await becomeAdvisor(page, currentProjectId); // A remplacer par une fixture avec un user déjà advisor du dossier

      await page.goto(`/project/${currentProjectId}/actions`);

      await createTask(page, taskName, '', true);
      await expect(
        page.locator('[data-test-id="list-tasks-switch-button"]')
      ).toBeChecked();

      await expect(
        page.locator('[data-test-id="task-initial-comment"]')
      ).toBeAttached();
      await expect(
        page.getByText(currentResource.fields.subtitle as string).first()
      ).toBeVisible();
      await expect(
        page.getByText(currentResource.fields.title as string).first()
      ).toBeVisible();
    });
  }
);

// page recommandation
