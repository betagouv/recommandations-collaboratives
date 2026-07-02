import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';

const currentProject = projects[2];

test.describe(
  'I can invite a member',
  { tag: '@page-projet-presentation-inviter-partenaire' },
  () => {
    const invitedFullName = 'New Member';
    const invitedEmail = 'new.member@test.fr';
    const inviterFullName = 'Boba collectivité';
    const project = 'Friche numéro 2';

    test('goes to the overview page and invite a member', async ({
      loginAs,
    }) => {
      const page = await loginAs('collectivité2');
      const message = `Bonjour ${invitedFullName}, je t'invite à conseiller mon dossier ${project} ${invitedEmail}`;
      const sentNotification = `Un courriel d'invitation à rejoindre le dossier a été envoyé à ${invitedEmail}`;

      await page.goto(`/project/${currentProject.pk}`);

      await page.locator('[data-cy="invite-project-member-button"]').click();

      const email = page.locator('#invite-email').first(); // id dupliqué dans le DOM : jQuery/Cypress prenait le premier
      await email.fill(invitedEmail);
      await expect(email).toHaveValue(invitedEmail);

      const messageField = page.locator('#invite-message').first();
      await messageField.fill(message);
      await expect(messageField).toHaveValue(message);

      await page
        .locator('#invite-member-modal')
        .getByText("Envoyer l'invitation")
        .click({ force: true });
      await page.waitForTimeout(500);
      await expect(page.getByText(sentNotification).first()).toBeVisible();
    });

    test('can see a notification of the invitation on the project activity feed', async ({
      loginAs,
    }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/${currentProject.pk}`);
      await page
        .locator('[data-test-id="project-activity-link"]')
        .click({ force: true });
      await expect(
        page
          .locator('[data-test-id="project-activity-tracking-staff"]')
          .locator('[data-test-id="project-activity-notification"]')
          .first()
      ).toBeAttached();
      await expect(page.getByText(inviterFullName).first()).toBeVisible();
      await expect(page.getByText('a invité ').first()).toBeVisible();
      await expect(page.getByText(invitedEmail).first()).toBeVisible();
      await expect(
        page.getByText('en tant que demandeur ou partenaire').first()
      ).toBeVisible();
    });
  }
);
