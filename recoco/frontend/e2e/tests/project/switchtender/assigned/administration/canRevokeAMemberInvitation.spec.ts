import { expect, test } from '../../../../../fixtures';
import { authFile } from '../../../../../helpers/users';
import projects from '../../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can go to administration area of a project and revoke an invite for a member',
  { tag: '@page-projet-parametres-gestion-invitation' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to the administration tab of a project and revoke the member invitation', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator("[data-test-id='navigation-administration-tab']")
        .click({ force: true });
      await expect(page).toHaveURL(/\/administration/);

      await page.locator('[data-cy="button-invite-project-member"]').click();

      const email = page.locator('#invite-email').first(); // id dupliqué dans le DOM : jQuery/Cypress prenait le premier
      await email.fill('collectivitybyjean@test.fr');
      await expect(email).toHaveValue('collectivitybyjean@test.fr');

      const message = page.locator('#invite-message').first();
      await message.fill(
        `Bonjour collectivitybyjean@test.fr, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );
      await expect(message).toHaveValue(
        `Bonjour collectivitybyjean@test.fr, je t'invite à conseiller mon dossier ${currentProject.fields.name}`
      );

      await page
        .locator('#invite-member-modal')
        .getByText("Envoyer l'invitation")
        .click({ force: true });

      // Ligne d'invitation pour cet email dans la liste des invitations en attente
      const invitationList = page.locator(
        '[data-test-id="administration-member-invitation-list"] ~ ul'
      );
      const invitationItem = invitationList
        .locator('> li')
        .filter({ hasText: 'collectivitybyjean@test.fr' });

      await expect(invitationItem.first()).toBeVisible();

      await invitationItem
        .locator('#revoke-invite-member')
        .click({ force: true });
      await expect(
        page
          .getByText(
            `L'invitation de collectivitybyjean@test.fr a bien été supprimée.`
          )
          .first()
      ).toBeVisible();
    });
  }
);
