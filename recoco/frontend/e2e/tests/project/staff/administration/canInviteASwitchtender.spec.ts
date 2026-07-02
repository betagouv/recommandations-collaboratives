import { expect, test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import users from '../../../../../cypress/fixtures/users/users.json';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[1];
const userToInvite = users[3];

test.describe(
  'I can go to administration area of a project and invite a switchtender',
  { tag: '@page-projet-parametres-gestion-utilisateur' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration tab of a project and invite a switchtender', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/administration'));

      await page.getByText('Inviter un conseiller').first().click({ force: true });

      const email = page.locator('.invite-switchtender-modal-email');
      await email.fill(`${userToInvite.fields.email}`);
      await expect(email).toHaveValue(`${userToInvite.fields.email}`);

      const textarea = page.locator('.invite-switchtender-modal-textarea');
      await textarea.fill(
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier friche numéro 2`
      );
      await expect(textarea).toHaveValue(
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier friche numéro 2`
      );

      await page
        .locator('.invite-switchtender-modal-button')
        .click({ force: true });
      await expect(
        page
          .getByText(
            `Un courriel d'invitation à rejoindre le dossier a été envoyé à ${userToInvite.fields.email}`
          )
          .first()
      ).toBeVisible();

      await expect(
        page
          .locator(
            "[data-test-id='administration-advisor-invitation-list'] ~ ul > li",
            { hasText: userToInvite.fields.email }
          )
          .first()
      ).toBeVisible();
    });
  }
);
