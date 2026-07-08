import { test } from '@playwright/test';

import projects from '../../../../cypress/fixtures/projects/projects.json';
import { ProjectLocation } from '../../../helpers/tools/geolocation';
import { authFile } from '../../../helpers/users';

/**
 * To run these tests: launch the front end of the application before running the tests
 */
test.use({ storageState: authFile('bob') });

test.describe.skip(
  'I can see the location of a project on the project overview',
  { tag: '@page-projet-presentation-localisation' },
  () => {
    test(`displays a marker of the project coordinates if project coordinates are set`, async ({
      page,
    }) => {
      const currentProject = projects[15];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.checkMapLayerProjectCoordinates();
    });

    test(`displays a marker of the project location if project coordinates are not set and geolocation data is found for project location`, async ({
      page,
    }) => {
      const currentProject = projects[14];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.checkMapLayerProjectLocation();
    });

    test('displays the area of the commune if geolocation data is only found for the commune', async ({
      page,
    }) => {
      const currentProject = projects[11];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.checkMapLayerAreaCommune();
    });

    // TODO verify is this test is still relevant
    test.skip(`displays an area circle around the centroid of the commune if no geolocation data is found`, async ({
      page,
    }) => {
      // This case might only happen with older projects
      const currentProject = projects[12];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.checkMapLayerCircle();
    });

    test(`displays no area indicator if the project's commune is not provided`, async ({
      page,
    }) => {
      // This case might only happen with older projects
      const currentProject = projects[16];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.checkMapLayerCircle(false);
    });

    test(`opens a modal with an interactive map`, async ({ page }) => {
      const currentProject = projects[11];
      const projectLocation = new ProjectLocation(page);
      await page.goto(`/project/${currentProject.pk}`);
      await page.waitForTimeout(600);
      await projectLocation.openMapModal();
    });
  }
);
