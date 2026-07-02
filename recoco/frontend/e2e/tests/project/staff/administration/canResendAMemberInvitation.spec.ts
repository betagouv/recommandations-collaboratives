import { expect, test } from '@playwright/test';

import projects from '../../../../../cypress/fixtures/projects/projects.json';
import users from '../../../../../cypress/fixtures/users/users.json';
import { authFile } from '../../../../helpers/users';

const currentProject = projects[1];
const userToInvite = users[6];

const invitationRow =
  "[data-test-id='administration-member-invitation-list'] ~ ul > li";

test.describe(
  'I can go to administration area of a project and send back an invite for a member',
  { tag: '@page-projet-parametres-gestion-invitation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('goes to the administration tab of a project and send back the member invitation', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(new RegExp('/administration'));

      await page.locator('[data-cy="button-invite-project-member"]').click();

      const email = page.locator('#invite-email').first(); // id dupliqué dans le DOM : jQuery/Cypress prenait le premier
      await email.fill(`${userToInvite.fields.email}`);
      await expect(email).toHaveValue(`${userToInvite.fields.email}`);

      const message = page.locator('#invite-message').first();
      await message.fill(
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );
      await expect(message).toHaveValue(
        `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );

      await page
        .locator('#invite-member-modal')
        .getByText("Envoyer l'invitation")
        .click({ force: true });

      await expect(
        page.locator(invitationRow, { hasText: userToInvite.fields.email }).first()
      ).toBeVisible();
      await page
        .locator(invitationRow, { hasText: userToInvite.fields.email })
        .locator('#resend-invite-member')
        .first()
        .click({ force: true });
      // cy.contains(`Bobette@test.fr a bien été relancé par courriel.`)
    });
  }
);
