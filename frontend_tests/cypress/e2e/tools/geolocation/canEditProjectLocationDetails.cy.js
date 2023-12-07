import projects from '../../../fixtures/projects/projects.json'
import projectView from '../../../support/views/project'
import projectLocation from '../../../support/tools/geolocation'

/**
 * To run these tests: launch the front end of the application before running the tests
 * TODO: fix baseURL once notfications PR is merged
 */
let currentProject 
const projectOwner = "bob"
const address = "23 Rue Elise Gervais"
describe('I can edit the location details of a project on the project knowledge tab', () => {
    it('can access a page to set the project coordinates by entering an address', () => {
        currentProject = projects[12];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`)
        
        cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-accept-all"]').click().then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMissingCoordinatesMessage('exist')
            projectLocation.navigateToLocationEditPageFromOverview() // test link in Overview tab
            projectLocation.editProjectLocationUsingAddressField(address)
            projectLocation.saveProjectLocation()
            projectLocation.checkMapLayerProjectCoordinates()
            projectLocation.checkMissingCoordinatesMessage('not.exist')
        });
    })

    it.skip('can access a page to set the project coordinates by clicking on a map', () => {
		// TODO: fix this test: fix function `editProjectLocationUsingInteractiveMap`
        currentProject = projects[11];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`)
        
        cy.get('[data-test-id="fr-consent-banner"]').find('[data-test-id="button-consent-accept-all"]').click().then(() => {
            cy.wait(600);
            projectLocation.checkMissingCoordinatesMessage('exist')
            projectView.navigateToKnowledgeTab()
            projectLocation.navigateToLocationEditPage() // test link in Knowledge tab
            projectLocation.editProjectLocationUsingInteractiveMap()
            projectLocation.saveProjectLocation()
            projectView.navigateToOverviewTab()
            projectLocation.checkMapLayerProjectCoordinates()
            projectLocation.checkMissingCoordinatesMessage('not.exist')
        });
    })
})
