import projects from '../../../fixtures/projects/projects.json';
import projectView from '../../../support/views/project';
import projectLocation from '../../../support/tools/geolocation';

/**
 * To run these tests: launch the front end of the application before running the tests
 * TODO: fix baseURL once notfications PR is merged
 */
let currentProject;
const projectOwner = 'bob';
const address = '12 Rue Edouard Vaillant';
describe('I can edit the location details of a project on the project knowledge tab', () => {
  beforeEach(() => {
    cy.visit('/');
    cy.hideCookieBannerAndDjango();
  });

  it('can access a page to set the project coordinates by entering an address', () => {
    currentProject = projects[12];
    cy.login(projectOwner);
    cy.visit(`/project/${currentProject.pk}`);

    projectLocation.checkMissingCoordinatesMessage('exist');
    projectLocation.navigateToLocationEditPageFromOverview(); // test link in Overview tab
    projectLocation.editProjectLocationUsingAddressField(address);
    projectLocation.saveProjectLocation();
    projectLocation.checkMapLayerProjectCoordinates();
    projectLocation.checkMissingCoordinatesMessage('not.exist');
  });

  it('can access a page to set the project coordinates by clicking on a map', () => {
    currentProject = projects[11];
    cy.login(projectOwner);
    cy.visit(`/project/${currentProject.pk}`);

    projectLocation.checkMissingCoordinatesMessage('exist');
    projectView.navigateToKnowledgeTab();
    projectLocation.navigateToLocationEditPage(); // test link in Knowledge tab
    cy.log('-----editProjectLocationUsingInteractiveMap ');
    projectLocation.editProjectLocationUsingInteractiveMap();
    cy.log('-----saveProjectLocation ');
    projectLocation.saveProjectLocation();
    cy.log('-----navigateToOverviewTab ');
    projectView.navigateToOverviewTab();
    cy.log('-----checkMapLayerProjectCoordinates ');
    projectLocation.checkMapLayerProjectCoordinates();
    cy.log('-----checkMissingCoordinatesMessage ');
    projectLocation.checkMissingCoordinatesMessage('not.exist');
  });
});
