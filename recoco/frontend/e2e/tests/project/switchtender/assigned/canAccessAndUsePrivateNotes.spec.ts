import { expect, test } from '../../../../fixtures';
import { Editor } from '../../../../helpers/tools/editor';
import { authFile } from '../../../../helpers/users';
import projects from '../../../../../cypress/fixtures/projects/projects.json';

const currentProject = projects[1];

test.describe(
  'I can access and use private notes',
  {
    tag: [
      '@page-projet-espace-conseiller',
      '@page-projet-espace-conseiller-nouveau-message',
    ],
  },
  () => {
    test.use({ storageState: authFile('conseiller1') });

    test('goes to private notes', async ({ page }) => {
      await page.goto(`/project/${currentProject.pk}/suivi`);

      const now = new Date();

      const textarea = page.locator('textarea');
      await textarea.fill(`test : ${now}`);
      await expect(textarea).toHaveValue(`test : ${now}`);

      const editor = new Editor(page);
      await editor.writeMessage(`test : ${now}`);

      await page.getByText('Enregistrer').first().click({ force: true });

      await expect(page.getByText(`test : ${now}`).first()).toBeVisible();
    });
  }
);
