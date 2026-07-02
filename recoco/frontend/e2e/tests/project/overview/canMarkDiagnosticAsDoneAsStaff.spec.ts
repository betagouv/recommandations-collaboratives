import { expect, test } from '../../../fixtures';

test.describe(
  'I can mark project diagnostic done',
  {
    tag: [
      '@page-projet-presentation',
      '@page-projet-presentation-mark-diagnostic-done',
    ],
  },
  () => {
    test('display diagnostic button (as staff)', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/2/presentation`);
      const button = page.locator('[data-cy="button-diag-project-done"]');
      await expect(button).toBeVisible();
      await button.click();
      await expect(button).toHaveCount(0);
      await expect(
        page.locator('[data-cy="diag-project-done"]')
      ).toBeVisible();
    });

    test('do not display diagnostic button (as owner)', async ({ loginAs }) => {
      const page = await loginAs('bob');
      await page.goto(`/project/2/presentation`);
      await expect(
        page.locator('[data-cy="button-diag-project-done"]')
      ).toHaveCount(0);
    });

    test('do not display diagnostic button (as advisor)', async ({
      loginAs,
    }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/2/presentation`);
      await expect(
        page.locator('[data-cy="button-diag-project-done"]')
      ).toHaveCount(0);
    });
  }
);
