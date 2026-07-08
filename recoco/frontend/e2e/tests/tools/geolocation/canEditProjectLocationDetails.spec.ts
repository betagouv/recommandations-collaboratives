import { expect, test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { ProjectLocation } from '../../../helpers/tools/geolocation';
import { authFile } from '../../../helpers/users';
import { ProjectView } from '../../../helpers/views/project';

/**
 * To run these tests: launch the front end of the application before running the tests
 * TODO: fix baseURL once notfications PR is merged
 */
const address = '12 Rue Edouard Vaillant';

test.use({ storageState: authFile('bob') });

test.describe(
  'I can edit the location details of a project on the project knowledge tab',
  { tag: '@page-projet-presentation-localisation' },
  () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/');
    });

    test('can access a page to set the project coordinates by entering an address', async ({
      page,
    }) => {
      const currentProject = projects[12];
      const projectLocation = new ProjectLocation(page);

      await page.goto(`/project/${currentProject.pk}`);

      await projectLocation.checkMissingCoordinatesMessage(true);
      await projectLocation.navigateToLocationEditPageFromOverview(); // test link in Overview tab
      await projectLocation.editProjectLocationUsingAddressField(address);
      await projectLocation.saveProjectLocation();
      await projectLocation.checkMapLayerProjectCoordinates();
      await projectLocation.checkMissingCoordinatesMessage(false);
    });

    test('can access a page to set the project coordinates by clicking on a map', async ({
      page,
    }) => {
      const currentProject = projects[11];
      const projectView = new ProjectView(page);
      const projectLocation = new ProjectLocation(page);

      await page.goto(`/project/${currentProject.pk}`);

      await projectLocation.checkMissingCoordinatesMessage(true);
      await projectView.navigateToKnowledgeTab();
      await projectLocation.navigateToLocationEditPage(); // test link in Knowledge tab
      await projectLocation.editProjectLocationUsingInteractiveMap();
      await projectLocation.saveProjectLocation();
      await projectView.navigateToOverviewTab();
      await projectLocation.checkMapLayerProjectCoordinates();
      await projectLocation.checkMissingCoordinatesMessage(false);
    });
  }
);
