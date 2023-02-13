import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[1];

describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to public notes', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')
    })
})
