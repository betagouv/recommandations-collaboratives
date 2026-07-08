import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

test.describe(
  'I can edit project tags on overview page',
  { tag: '@page-projet-presentation-tags' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test.beforeEach(async ({ page }) => {
      await page.goto(`/project/1`);
    });

    test('adds new tags on project overview', async ({ page }) => {
      await page.locator('[data-cy="overview-add-project-tag"]').click();
      await page.locator('#id_tags').fill('new-tag');
      await page.locator('[data-cy="btn-submit-project-tag"]').click();
      await expect(page).toHaveURL(/\/project\/1\/presentation/);
      await expect(page.locator('[data-cy="container-tags"]')).toContainText(
        'new-tag'
      );
      await page.locator('[data-cy="overview-edit-project-tag"]').click();
      await page.locator('#id_tags').clear();
      await page.locator('[data-cy="btn-submit-project-tag"]').click();
      await expect(page).toHaveURL(/\/project\/1\/presentation/);
      await expect(
        page.locator('[data-cy="container-tags"]')
      ).toHaveCount(0);
    });
  }
);
