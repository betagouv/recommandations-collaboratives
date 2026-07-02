import { expect, test } from '../../../fixtures';

test.describe(
  'I can not see owner contact',
  { tag: '@page-projet-presentation' },
  () => {
    test('display owner contact (as staff)', async ({ loginAs }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/2/presentation`);
      await expect(
        page.locator('[data-cy="container-revealed-contact"]')
      ).toContainText('bob@test.fr');
    });

    test('display owner contact (as owner)', async ({ loginAs }) => {
      const page = await loginAs('bob');
      await page.goto(`/project/2/presentation`);
      await expect(
        page.locator('[data-cy="container-revealed-contact"]')
      ).toContainText('bob@test.fr');
    });

    test('display hiden owner contact (as advisor)', async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto(`/project/2/presentation`);
      await expect(
        page.locator('[data-cy="container-revealed-contact"]')
      ).toBeHidden();
      await page.locator('[data-cy="btn-overview-reveal-contact"]').click();
      await expect(
        page.locator('[data-cy="container-revealed-contact"]')
      ).toContainText('bob@test.fr');
      await page.reload();
      await expect(
        page.locator('[data-cy="container-revealed-contact"]')
      ).toContainText('bob@test.fr');
    });
  }
);
