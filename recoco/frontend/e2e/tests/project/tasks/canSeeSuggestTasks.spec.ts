import { expect, test } from '../../../fixtures';
import { becomeAdvisor } from '../../../helpers/commands';
import projects from '../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

// TODO Réécrire : la redirection /actions → /conversations#actions ne contient plus le bouton see-suggest-task-button
test.describe.skip(
  'I can see suggest task',
  { tag: '@page-projet-recommandations' },
  () => {
    test('as advisor I can see ', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/${currentProject.pk}`);
      await becomeAdvisor(page, currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du dossier
      await page.goto(`/project/${currentProject.pk}/actions`);
      await page.locator('[data-test-id="see-suggest-task-button"]').click();
      await expect(page).toHaveURL(/\/suggestions/);
    });

    test('as staff I can see ', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/${currentProject.pk}`);
      await becomeAdvisor(page, currentProject.pk); // A remplacer par une fixture avec un user déjà advisor du dossier
      await page.goto(`/project/${currentProject.pk}/actions`);
      await page.locator('[data-test-id="see-suggest-task-button"]').click();
      await expect(page).toHaveURL(/\/suggestions/);
    });
  }
);

// page recommandations
