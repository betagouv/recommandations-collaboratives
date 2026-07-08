import { test } from '../../../fixtures';
import { createProject } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

test.describe('I can follow a project', { tag: '@deposer-projet' }, () => {
  test.use({ storageState: authFile('collectivité1') });

  test('goes to the homepage and create a project with the main CTA', async ({
    page,
  }) => {
    await createProject(page, 'fake project name');
  });
});
