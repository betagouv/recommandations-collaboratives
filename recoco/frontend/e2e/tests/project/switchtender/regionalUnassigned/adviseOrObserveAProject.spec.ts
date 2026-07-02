import { test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can advice a project',
  {
    tag: ['@navigation-projet', '@page-projet-parametres-gestion-utilisateur'],
  },
  () => {
    test.use({ storageState: authFile('conseiller2') });

    test.skip('goes to overview page and advise the project', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);

      // cy.contains("Conseiller ce dossier").click({ force: true })
      // cy.wait(500);
      // cy.contains("Ne plus conseiller ce dossier")
      // cy.contains("Jeanne Conseille")
    });
  }
);
