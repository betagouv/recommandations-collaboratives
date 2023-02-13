import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[3];

describe("I can access overview page and can't see the synopsis", () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it("goes to overview page and can't see synopsis", () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.contains("Reformulation du besoin").should('not.exist')
    })
})
