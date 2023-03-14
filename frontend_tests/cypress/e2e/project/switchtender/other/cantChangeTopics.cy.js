import projects from '../../../../fixtures/projects/projects.json'

const currentProject = projects[2];

describe("I can't change topics of a project I don't advise", () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it("goes to overview page and should not see edit topic button", () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.url().should('include', '/presentation')

        cy.contains("Identifier les sujets").should('not.exist')
    })
})
