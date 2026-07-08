import { expect, test } from '../../../../fixtures';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can see and update an advisor note',
  { tag: '@page-projet-presentation-note-interne' },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to project overview and update advisor note', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);

      await expect(
        page.getByText('Note interne aux conseillers').first()
      ).toBeVisible();

      await page
        .locator('[data-cy="edit-internal-note"]')
        .click({ force: true });

      const now = new Date();

      const textarea = page.locator('textarea');
      await textarea.clear();

      await textarea.fill(`test : ${now}`);
      await expect(textarea).toHaveValue(`test : ${now}`);

      await page.getByText('Enregistrer').first().click({ force: true });

      await expect(page.getByText(`test : ${now}`).first()).toBeVisible();
    });
  }
);
