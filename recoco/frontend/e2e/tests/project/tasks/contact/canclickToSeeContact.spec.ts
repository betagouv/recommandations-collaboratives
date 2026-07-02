import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';

test.describe.skip(
  'I can see contacts information',
  { tag: '@page-projet-recommandations-modal' },
  () => {
    test.use({ storageState: authFile('bob') });

    test('click to see contat info and doesnt have to click again', async ({
      page,
    }) => {
      await page.goto(`/ressource/2`);
      const buttons = page.locator('[data-test-id="see-contact-info-button"]');
      const count = await buttons.count();
      for (let i = 0; i < count; i++) {
        await buttons.nth(i).click({ force: true });
      }
      for (let i = 0; i < count; i++) {
        await expect(buttons.nth(i)).toBeHidden();
      }
      await page.goto(`/ressource/2`);
      const buttonsAfterReload = page.locator(
        '[data-test-id="see-contact-info-button"]'
      );
      const countAfterReload = await buttonsAfterReload.count();
      for (let i = 0; i < countAfterReload; i++) {
        await expect(buttonsAfterReload.nth(i)).toBeHidden();
      }
    });
  }
);
