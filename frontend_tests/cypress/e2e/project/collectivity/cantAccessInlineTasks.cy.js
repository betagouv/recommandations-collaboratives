import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe("I can go to action page but can't see the loop to access the inline tasks", () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it("goes to action page and can't see inline tasks loop button", () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')
        cy.get('#tasks-inline-button').should('not.exist');
    })
})
