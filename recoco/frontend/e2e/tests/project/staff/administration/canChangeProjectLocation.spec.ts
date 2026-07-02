import { expect, test } from '@playwright/test';

import commune from '../../../../../cypress/fixtures/geomatics/commune.json';
import projects from '../../../../../cypress/fixtures/projects/projects.json';
import { authFile } from '../../../../helpers/users';

const currentCommune = commune[1];

const currentProject = projects[1];

test.describe(
  'I can go to administration area of a project and change the project location',
  {
    tag: [
      '@page-projet-parametres-modifier',
      '@page-projet-presentation-localisation',
    ],
  },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration tab of a project and change the project location', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/administration'));

      const address = page.locator('#input-project-address').first();
      await address.fill(`${currentProject.fields.location} updated`);
      await expect(address).toHaveValue(
        `${currentProject.fields.location} updated`
      );

      const postcode = page.locator('[name=postcode]');
      // Le champ postcode alimente l'autocomplétion commune (debounce). La
      // frappe peut partir avant l'hydratation Alpine : on retape jusqu'à ce
      // que la commune correspondante apparaisse dans le select.
      await expect(async () => {
        await postcode.fill('');
        await postcode.pressSequentially(currentCommune.fields.insee);
        // fetchCities écoute l'événement change : en Cypress il partait au
        // blur, quand le focus passait au champ suivant.
        await postcode.blur();
        await expect(
          page.locator(
            `select[name="insee"] option[value="${currentCommune.fields.insee}"]`
          )
        ).toBeAttached({ timeout: 3_000 });
      }).toPass({ timeout: 20_000 });
      await expect(postcode).toHaveValue(currentCommune.fields.insee);

      const name = page.locator('#id_name');
      await name.fill(`${currentProject.fields.name} updated`);
      await expect(name).toHaveValue(`${currentProject.fields.name} updated`);

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

      // cy.contains n'assertait que l'existence (le texte est dans un bloc masqué)
      await expect(
        page.getByText(`${currentCommune.fields.insee}`).first()
      ).toBeAttached();
      await expect(
        page.getByText(`${currentCommune.fields.name}`).first()
      ).toBeAttached();
    });
  }
);
