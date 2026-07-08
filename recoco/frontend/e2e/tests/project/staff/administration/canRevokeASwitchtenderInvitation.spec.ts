import { expect, test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import users from '../../../../../cypress/fixtures/users/users.json';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[1];
const userToInvite = users[3];

const invitationRow =
  "[data-test-id='administration-advisor-invitation-list'] ~ ul > li";

test.describe(
  'I can go to administration area of a project and revoke an invite for a switchtender',
  { tag: '@page-projet-parametres-gestion-invitation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration tab of a project and revoke the switchtender invitation', async ({
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
        page.locator(invitationRow, { hasText: userToInvite.fields.email }).first()
      ).toBeVisible();

      await page
        .locator(invitationRow, { hasText: userToInvite.fields.email })
        .locator('#revoke-invite-switchtender')
        .first()
        .click({ force: true });
      await expect(
        page
          .getByText(`L'invitation de jeannot@test.fr a bien été supprimée.`)
          .first()
      ).toBeVisible();
    });
  }
);
