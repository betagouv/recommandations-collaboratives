import { expect, test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can go to administration area of a project and change general information',
  { tag: '@page-projet-parametres-modifier' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration tab of a project general information', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/administration'));

      const name = page.locator('#id_name');
      await name.fill(`${currentProject.fields.name} updated`);
      await expect(name).toHaveValue(`${currentProject.fields.name} updated`);

      const description = page.locator('#input-project-description');
      await description.fill(`${currentProject.fields.description} updated`);
      await expect(description).toHaveValue(
        `${currentProject.fields.description} updated`
      );

      // Le clic de soumission peut partir avant l'hydratation Alpine : on
      // re-clique jusqu'à la redirection.
      await expect(async () => {
        await page
          .getByText('Modifier les informations du dossier')
          .click({ force: true });
        await expect(page).toHaveURL(new RegExp('/presentation'), {
          timeout: 3_000,
        });
      }).toPass({ timeout: 15_000 });

      await expect(
        page.getByText(`${currentProject.fields.description} updated`).first()
      ).toBeVisible();
    });
  }
);
