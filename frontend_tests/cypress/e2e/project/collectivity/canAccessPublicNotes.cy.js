import project from '../../../fixtures/projects/project.json'
const index = 10

describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("bob");
        cy.createProject(index);
        cy.logout();
        cy.approveProject(index);
        cy.login("bob");
        cy.navigateToProject(index);
    })

    it('clicks on the "public note" button', () => {

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')
    })
})
