import project from '../../../../cypress/fixtures/projects/project.json';
import { test } from '../../../fixtures';
import { createProject } from '../../../helpers/commands';
import { authFile } from '../../../helpers/users';

test.describe(
  "I can create a project if i'm connected",
  { tag: ['@deposer-projet', '@critical'] },
  () => {
    test.use({ storageState: authFile('collectivité1') });

    test('goes to the onboarding process step by step and create a project ', async ({
      page,
    }) => {
      await createProject(page, 'Coucou');
    });

    test('goes to the onboarding process step by step and create a project without any adress ', async ({
      page,
    }) => {
      await createProject(page, 'Project without location', {
        ...project,
        name: 'Friche nomade',
        location: '',
        postcode: 42424,
        description: 'Je suis une friche nomade',
      });
    });
  }
);
