import { expect, test } from '../../fixtures';
import { waitForAlpine } from '../../helpers/commands';
import { authFile } from '../../helpers/users';

const now = new Date();

const resource = {
  title: 'Nouvelle ressource de test',
  subtitle: 'Soustitre de la ressource de test',
  summary: `test : ${now}`,
  deparments: {
    index: 1,
    name: 'Département de test numéro 2',
  },
  tags: 'etiquette1',
  expires_on: '2022-12-20',
};

test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

test.describe(
  'I can edit a resource as a staff',
  { tag: '@acces-ressources' },
  () => {
    test('edits a resource', async ({ page }) => {
      await page.goto('/ressource/1/');
      await page.locator('[data-test-id="edit-resource"]').click();
      await expect(page).toHaveURL(/\/ressource\/1\/update\//);
      // Le formulaire est soumis depuis le store Alpine (x-model) : attendre
      // l'hydratation avant de remplir, sinon les valeurs sont perdues.
      await waitForAlpine(page);

      const title = page.locator('#id_title');
      // init() recharge les champs depuis l'API : toute saisie antérieure à
      // cette réponse serait écrasée — attendre que le formulaire soit peuplé.
      await expect(title).not.toHaveValue('');
      await title.fill(resource.title);
      await expect(title).toHaveValue(resource.title);

      const subtitle = page.locator('#id_subtitle');
      await subtitle.fill(resource.subtitle);
      await expect(subtitle).toHaveValue(resource.subtitle);

      const summary = page.locator('#id_summary');
      await summary.fill(resource.summary);
      await expect(summary).toHaveValue(resource.summary);

      const tags = page.locator('#id_tags');
      await tags.fill(resource.tags);
      await expect(tags).toHaveValue(resource.tags);

      const expiresOn = page.locator('#id_expires_on');
      await expiresOn.fill(resource.expires_on);
      await expect(expiresOn).toHaveValue(resource.expires_on);

      // Le clic peut partir avant l'hydratation Alpine : on re-clique
      // jusqu'à quitter la page d'édition.
      await expect(async () => {
        await page
          .locator('[data-test-id="publish-resource-btn"]')
          .click({ force: true });
        await expect(page).not.toHaveURL(/update/, { timeout: 3_000 });
      }).toPass({ timeout: 15_000 });

      await expect(page).toHaveURL(/\/ressource\//);

      await expect(page.getByText(resource.title).first()).toBeVisible();
      await expect(page.getByText(resource.subtitle).first()).toBeVisible();
      await expect(page.getByText(resource.summary).first()).toBeVisible();
      await expect(page.getByText(resource.tags).first()).toBeVisible();
    });
  }
);
