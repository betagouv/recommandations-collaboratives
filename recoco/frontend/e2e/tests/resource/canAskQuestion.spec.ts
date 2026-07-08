import { expect, test } from '../../fixtures';
import { checkCaptcha } from '../../helpers/commands';
import { authFile } from '../../helpers/users';

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can ask a question on a resource',
  { tag: '@acces-ressources' },
  () => {
    test('asks a question', async ({ page }) => {
      await page.goto('/ressource/3/');

      await page.getByText('Poser une question').first().click({ force: true });
      await expect(page).toHaveURL(/\/contact\//);
      await expect(
        page.getByText("Contacter l'équipe example").first()
      ).toBeVisible();

      const content = page.locator('#input-project-content');
      await content.fill('Question sur la resource numéro 3');
      await expect(content).toHaveValue('Question sur la resource numéro 3');

      await checkCaptcha(page, 500);

      await page.getByText('Envoyer mon message').first().click({ force: true });
      await expect(page).toHaveURL(/\/ressource\/3\//);
    });
  }
);
