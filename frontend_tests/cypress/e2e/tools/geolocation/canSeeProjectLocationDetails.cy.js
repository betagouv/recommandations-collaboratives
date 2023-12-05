import projects from '../../../fixtures/projects/projects.json'
import projectLocation from '../../../support/tools/geolocation'

/**
 * To run these tests: launch the front end of the application before running the tests
 * TODO: fix baseURL once notfications PR is merged
 */
let currentProject
const projectOwner = "bob"
describe('I can see the location of a project on the project overview', () => {

    it(`displays a marker of the project coordinates if project coordinates are set`, () => {
        currentProject = projects[15];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMapLayerProjectCoordinates()
        });
    })

    it.skip(`displays a marker of the project location if project coordinates are not set and geolocation data is found for project location`, () => {

        // FAILING
        currentProject = projects[14];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMapLayerProjectLocation()
        });
    })

    it('displays the area of the commune if geolocation data is only found for the commune', () => {
        currentProject = projects[11];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMapLayerAreaCommune()
        });
    })

    it(`displays an area circle around the centroid of the commune if no geolocation data is found`, () => {
        // This case might only happen with older projects
        currentProject = projects[12];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMapLayerCircle()
        });
    })

    it(`displays no area indicator if the project's commune is not provided`, () => {
        // This case might only happen with older projects
        currentProject = projects[16];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.checkMapLayerCircle('not.exist')
        });
    })

    it(`opens a modal with an interactive map`, () => {
       currentProject = projects[11];
        cy.login(projectOwner);
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(600); // TODO: fix by testing loading state (+ add loading spinner)
            projectLocation.openMapModal()
        });
    })
})
