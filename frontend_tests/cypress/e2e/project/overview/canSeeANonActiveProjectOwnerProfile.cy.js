import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[9];

describe('I can go to overview tab', () => {
    beforeEach(() => {
        cy.login("staff");
    })


    it('show the profile of a non active project owner with the correct class', () => {
        cy.visit(`/project/${currentProject.pk}`)

        cy.get('[data-test-id="project-owner-name-details"]').should('have.class', 'inactive-status')
    })
})
