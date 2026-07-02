import project from '../../../../cypress/fixtures/projects/project.json';
import { expect, test } from '../../../fixtures';
import { createProject } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

const projectName = 'New project onboarding answer';

test.describe.configure({ mode: 'serial' });

test.describe(
  'I can see onboarding answer on the overview tab',
  { tag: '@page-projet-presentation' },
  () => {
    let projetId: string;

    test.beforeAll(async ({ browser }) => {
      const context = await browser.newContext({
        storageState: authFile('collectivité1'),
      });
      const page = await context.newPage();
      projetId = await createProject(page, projectName);
      await context.close();
    });

    test('should see the project description on overview tab as staff', async ({
      loginAs,
    }) => {
      const page = await loginAs('staff'); // TODO replace by staffOnSite and check behaviour
      await page.goto(`/project/${projetId}`);
      await expect(
        page.locator('[data-test-id="project-information-card-context"]')
      ).toContainText(project.description);
    });

    test('should see the project description on overview tab as collectivity', async ({
      loginAs,
    }) => {
      const page = await loginAs('collectivité1');
      await page.goto(`/project/${projetId}`);
      await expect(
        page.locator('[data-test-id="project-information-card-context"]')
      ).toContainText(project.description);
    });

    // TODO add fixture for complete questions onboarding
  }
);
