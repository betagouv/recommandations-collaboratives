import projects from '../../../fixtures/projects/projects.json'
const currentProject = projects[1];

describe('I can access actions tab in a project as a member', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to the action page of my project', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.contains('Recommandations').click({ force: true })
        cy.url().should('include', '/actions')

    })
})
