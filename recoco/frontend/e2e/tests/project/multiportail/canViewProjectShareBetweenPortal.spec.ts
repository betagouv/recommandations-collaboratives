import { expect, test } from '../../../fixtures';

test.describe(
  'Project share between portal',
  { tag: '@page-projet-presentation' },
  () => {
    test('display share by and with portal on kanban', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto('/projects');
      // cy.get(...).should('be.visible') passe si AU MOINS un élément de la
      // collection est visible (jQuery :is(':visible')). Les cartes masquées par
      // x-show apparaissent en premier dans le DOM, donc on filtre sur visible.
      const sharedByOrigin = page
        .locator('[data-cy="kanban-project-shared-by-origin"]')
        .filter({ visible: true });
      await expect(sharedByOrigin.first()).toBeVisible();
      await expect(sharedByOrigin.first()).toContainText('example2');
      const sharedWith = page
        .locator('[data-cy="kanban-project-shared-with"]')
        .filter({ visible: true });
      await expect(sharedWith.first()).toBeVisible();
      await expect(sharedWith.first()).toContainText('example3');
    });

    test('display share by portal on moderation', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto('/projects/moderation');
      const sharedBy = page.locator('[data-cy="moderation-folder-shared-by"]');
      await expect(sharedBy.first()).toBeVisible();
      await expect(sharedBy.first()).toContainText('example2');
    });

    test('display current portal EDL first', async ({ loginAs }) => {
      const page = await loginAs('collectivité1');
      await page.goto('/project/23/connaissance');

      await expect(
        page.locator('[data-cy="survey-name"]').first()
      ).toContainText('Questionnaire example');
    });
  }
);
