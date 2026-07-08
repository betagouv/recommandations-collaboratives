import { expect, test } from '../../../fixtures';

// TODO Réécrire : la création de tâche redirige désormais vers /conversations
test.describe.skip(
  'I can attach miscellanious ressource to task',
  {
    tag: [
      '@page-projet-recommandations-creation',
      '@page-projet-recommandations',
    ],
  },
  () => {
    test('publishes a task with resource comment / no comment', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller1');

      await page.goto(`/projects/action/?project_id=25&resource_id=2`);
      await expect(
        page.locator('[data-test-id="publish-draft-task-button"]')
      ).toBeEnabled();
      await expect(
        page.locator('[data-cy="button-submit-task"]')
      ).toBeEnabled();
      await expect(
        page.locator('[data-cy="reco-pusher-selected-project"]')
      ).toContainText(
        'commune de test - Projet avec une reco qui a une resource qui a des contacts'
      );

      await expect(
        page.locator('[data-cy="radio-push-reco-single-resource"]')
      ).toBeChecked();

      await page
        .locator('[data-test-id="search-resource-input"]')
        .pressSequentially('res');
      await page
        .locator('[data-cy="radio-resource-list-task"]')
        .first()
        .check({ force: true });

      // Test with no comment
      await expect(
        page.locator('[data-cy="button-submit-task"]')
      ).toBeEnabled();

      // Test with comment
      await page.locator('.ProseMirror p').click();
      await page.keyboard.type('text');

      await expect(
        page.locator('[data-cy="button-submit-task"]')
      ).toBeEnabled();
      await page.locator('[data-cy="button-submit-task"]').click();

      await expect(page).toHaveURL(/\/actions/);
    });

    test('cannot select a draft resource and see warning', async ({
      loginAs,
    }) => {
      const page = await loginAs('staff');
      await page.goto(`/projects/action/?project_id=25`);

      await expect(
        page.locator('[data-cy="radio-push-reco-single-resource"]')
      ).toBeChecked();

      await page
        .locator('[data-test-id="search-resource-input"]')
        .pressSequentially('brouillon');
      await expect(
        page.locator('[data-cy="resource-warning-status-draft"]')
      ).toBeVisible();
      await expect(
        page.locator('[data-cy="radio-resource-list-task"]').first()
      ).toBeDisabled();
    });

    test.skip('publishes a task with external resource', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/projects/action/?project_id=25`);

      const externalRadio = page.locator(
        '[data-cy="radio-push-reco-external-resource"]'
      );
      await expect(externalRadio).not.toBeChecked();
      await externalRadio.check({ force: true });
      await expect(externalRadio).toBeChecked();

      await page
        .locator('[data-cy="input-external-resource-url"]')
        .fill(
          'https://wiki.resilience-territoire.ademe.fr/wiki/Comment_partager_la_connaissance_et_documentation_dans_le_commun_%3F'
        );
      await page.locator('[data-cy="button-external-resource-load"]').click();
      await page
        .locator('[data-cy="radio-resource-list-task"]')
        .check({ force: true });

      await page.locator('.ProseMirror p').click();
      await page.keyboard.type('text');

      await expect(
        page.locator('[data-cy="button-submit-task"]')
      ).toBeEnabled();
      await page.locator('[data-cy="button-submit-task"]').click();

      await expect(page).toHaveURL(/\/actions/);
    });

    test('publishes a task with no resource', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/projects/action/?project_id=25`);

      const noResourceRadio = page.locator(
        '[data-cy="radio-push-reco-no-resource"]'
      );
      await expect(noResourceRadio).not.toBeChecked();
      await noResourceRadio.check({ force: true });
      await expect(noResourceRadio).toBeChecked();

      await page.locator('.ProseMirror p').click();
      await page.keyboard.type('text');

      await page
        .locator('[data-cy="input-title-task"]')
        .fill('reco test with no resource');
      await expect(
        page.locator('[data-cy="button-submit-task"]')
      ).toBeEnabled();
      await page.locator('[data-cy="button-submit-task"]').click();

      await expect(page).toHaveURL(/\/actions/);
    });
  }
);
