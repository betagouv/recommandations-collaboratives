import projects from '../../../../cypress/fixtures/projects/projects.json';
import { expect, test } from '../../../fixtures';
import { authFile } from '../../../helpers/users';

const currentProject = projects[1];

test.describe(
  'I can go to overview tab',
  { tag: '@page-projet-presentation' },
  () => {
    test.use({ storageState: authFile('staff') }); // TODO replace by staffOnSite and check behaviour

    test('see the project phone if no project owner phone number', async ({
      page,
    }) => {
      await page.goto(`/project/${currentProject.pk}`);

      //Used to match phone logic returned from django
      await expect(
        page.getByText(`${currentProject.fields.phone}`).first()
      ).toBeVisible();
    });
  }
);
