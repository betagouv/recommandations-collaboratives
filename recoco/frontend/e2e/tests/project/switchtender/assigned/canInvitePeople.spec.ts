import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe('I can invite people', { tag: '@bouton-inviter-projet' }, () => {
  test.use({ storageState: authFile('conseiller1') });

  test('goes to share a project page', async ({ page }) => {
    await page.goto(`/project/${currentProject.pk}`);

    await page.locator('[data-cy="invite-project-member-button"]').click();

    const email = page.locator('#invite-email').first(); // id dupliqué dans le DOM : jQuery/Cypress prenait le premier
    await email.fill('member@test.fr');
    await expect(email).toHaveValue('member@test.fr');

    const message = page.locator('#invite-message').first();
    await message.fill(
      "Bonjour membre, je t'invite à conseiller mon dossier friche numéro 2"
    );
    await expect(message).toHaveValue(
      "Bonjour membre, je t'invite à conseiller mon dossier friche numéro 2"
    );

    await page
      .locator('#invite-member-modal')
      .getByText("Envoyer l'invitation")
      .click({ force: true });
    await expect(
      page
        .getByText(
          "Un courriel d'invitation à rejoindre le dossier a été envoyé à member@test.fr"
        )
        .first()
    ).toBeVisible();
  });
});
