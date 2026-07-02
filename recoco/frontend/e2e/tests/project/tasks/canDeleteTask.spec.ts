import { expect, test } from '../../../fixtures';
import { becomeAdvisor, createTask } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';
import projects from '../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

// TODO Réécrire : open-task-actions-button et delete-task-action-button n'existent plus (task_actions.html supprimé)
test.describe.skip(
  'I can go to tasks tab',
  {
    tag: [
      '@page-projet-recommandations',
      '@page-projet-recommandations-suppression',
    ],
  },
  () => {
    test.use({ storageState: authFile('conseiller1') });
    // cy.createProject('delete task');

    test('deletes a task', async ({ page }) => {
      await becomeAdvisor(page, currentProject.pk);
      await page.goto(`/project/${currentProject.pk}/actions`);

      await createTask(page, 'test');

      await expect(
        page.locator('[data-test-id="list-tasks-switch-button"]')
      ).toBeChecked();

      const count = await page
        .locator('[data-test-id="open-task-actions-button"]')
        .count();

      await page
        .locator('[data-test-id="open-task-actions-button"]')
        .first()
        .click({ force: true });
      await page
        .locator('[data-test-id="delete-task-action-button"]')
        .first()
        .click({ force: true });
      await page
        .locator('[data-test-id="delete-task-modal-button"]')
        .click({ force: true });

      await expect(
        page.locator('[data-test-id="open-task-actions-button"]')
      ).toHaveCount(count - 1);

      // the first test try to see if there are no tasks
      // Now we test if the list have one element less
      // cy.get('[data-test-id="no-tasks-banner"]').should('exist');
    });
  }
);

// page recommandations
