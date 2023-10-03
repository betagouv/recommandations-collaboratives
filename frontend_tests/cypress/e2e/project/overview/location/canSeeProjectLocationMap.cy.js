import projects from '../../../../fixtures/projects/projects.json'


describe('I can see the location of a project on the project overview', () => {
    beforeEach(() => {
        cy.login("jean");
    })


    it(`displays no area indicator if the project's commune is not provided`, () => {
        const currentProject = projects[10];
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.get('[data-test-id="project-map-static"]').find('.leaflet-overlay-pane').then(() => {
                cy.get('.area-circle').should('not.exist');
            });
        })
    })

    it(`displays an area circle around the centroid of the commune if geolocation does not exist `, () => {
        const currentProject = projects[1];
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.get('[data-test-id="project-map-static"]').find('.leaflet-overlay-pane').find('.area-circle');
        })
    })

    it('displays the area of the commune if geolocation data exists', () => {
        const currentProject = projects[9];
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.get('[data-test-id="project-map-static"]').find('.leaflet-overlay-pane').then(() => {
                // TODO: find a way to test commune area overlay
                cy.get('.area-circle').should('not.exist');
            });
        })
    })

    it(`opens a modal with an interactive map`, () => {
        const currentProject = projects[9];
        cy.visit(`/project/${currentProject.pk}`).then(() => {
            cy.wait(500); // TODO: fix by testing loading state (+ add loading spinner)
            cy.get('[data-test-id="project-location"]').find('[data-test-id="toggle-open-map-modal"]').click({force: true});
            cy.get('[data-test-id="project-map-interactive"]').find('.leaflet-control-zoom')
        });
    })
})
