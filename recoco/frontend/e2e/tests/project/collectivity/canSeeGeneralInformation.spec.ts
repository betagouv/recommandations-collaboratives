import projects from '../../../../cypress/fixtures/projects/projects.json';
import users from '../../../../cypress/fixtures/users/users.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];
const currentUser = users[4];

test.describe(
  'I can see general informations',
  { tag: '@page-projet-presentation' },
  () => {
    test.use({
      storageState: authFile(currentUser.fields.first_name.toLowerCase()),
    });

    test('goes to the overview page and read project informations', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await expect(page.getByText(currentProject.fields.name).first()).toBeVisible();
      await expect(
        page.getByText(currentProject.fields.description).first()
      ).toBeVisible();

      await expect(page.getByText('Bob Collectivité').first()).toBeVisible();
      // cy.contains n'assertait que l'existence : l'email est un lien mailto
      // masqué dans la carte contact.
      await expect(
        page.getByText(currentUser.fields.email).first()
      ).toBeAttached();
      await expect(
        page.getByText(currentUser.fields.first_name).first()
      ).toBeVisible();
      await expect(
        page.getByText(currentUser.fields.last_name).first()
      ).toBeVisible();
      await expect(
        page.getByText('Organisation de test').first()
      ).toBeVisible();
      await expect(page.getByText('bob@test.fr').first()).toBeAttached();
      await expect(page.getByText('01 01 01 01 01').first()).toBeVisible();

      await expect(page.getByText('Jean Conseille').first()).toBeVisible();

      await expect(page.getByText('Bob Collectivité').first()).toBeVisible();
    });
  }
);
