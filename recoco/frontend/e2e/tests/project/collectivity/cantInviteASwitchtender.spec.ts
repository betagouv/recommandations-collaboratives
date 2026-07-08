import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[2];

test.describe(
  'I cannot invite a switchtender as a collectivity',
  { tag: '@page-projet-presentation-inviter-suivie' },
  () => {
    test.use({ storageState: authFile('collectivité2') });

    test('goes to the overview page and not show the switchtender invite button', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);
      await expect(page).toHaveURL(/\/presentation/);
      await expect(page.getByText(currentProject.fields.name).first()).toBeVisible();
      await expect(
        page.getByText('Inviter un conseiller').first().first()
      ).toBeHidden();
    });
  }
);
