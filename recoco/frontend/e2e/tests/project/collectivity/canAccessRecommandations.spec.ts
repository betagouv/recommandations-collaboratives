import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { createTask } from '../../../helpers/commands';

const currentProject = projects[1];

// TODO Réécrire : badge-new-task, close-modal-task, banner-new-tasks ont été supprimés avec la preview modal
test.describe.skip(
  'I can access the recommandations',
  { tag: '@page-projet-recommandations' },
  () => {
    test('goes to recommandations tab and see new recommandations', async ({
      loginAs,
    }) => {
      const advisorPage = await loginAs('conseiller1');
      await advisorPage.goto(`/project/${currentProject.pk}/actions`);
      await createTask(advisorPage, 'Notif test');

      const page = await loginAs('collectivité1');
      await page.goto(`/project/${currentProject.pk}/actions`);
      await expect(page.locator('Ajouter une recommandation')).toHaveCount(0);

      // TODO : using intercept and dynamic wait
      // cy.intercept(
      //   'POST',
      //   /\/api\/projects\/\d+\/tasks\/\d+\/notifications\/mark_all_as_read\/$/,
      //   'success'
      // ).as('markVisited');

      const badge = page.locator('[data-test-id="badge-new-task"]');
      await expect(badge.first()).toBeAttached();
      await badge.first().click({ force: true });
      // TODO : using intercept and dynamic wait
      // cy.wait('@markVisited');
      await page.waitForTimeout(500);
      const closeModal = page.locator('[data-test-id="close-modal-task"]');
      await expect(closeModal.first()).toBeAttached();
      await closeModal.first().click({ force: true });
      await expect(
        page.locator('[data-test-id="banner-new-tasks"]')
      ).toHaveCount(0);
      await expect(
        page.locator('[data-test-id="badge-new-task"]').first()
      ).toBeHidden();
    });
  }
);
