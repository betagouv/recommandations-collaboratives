import { expect, test } from '../../fixtures';

test.describe(
  'I can create a new project from the main header project list dropdown',
  { tag: '@deposer-projet' },
  () => {
    test('display button as a collectivity', async ({ loginAs }) => {
      const page = await loginAs('collectivité1');
      await page.goto('/');
      const createButton = page.locator('[data-test-id="create-project"]');
      await expect(createButton.first()).toBeAttached();
      await createButton.click({ force: true });
      await expect(page).toHaveURL(/\/onboarding/);
    });

    test("don't display button as an advisor", async ({ loginAs }) => {
      const page = await loginAs('conseiller1');
      await page.goto('/');
      await expect(
        page.locator('[data-test-id="create-project"]')
      ).toHaveCount(0);
    });
  }
);
