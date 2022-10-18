describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to public notes', () => {

        cy.visit('/project/2')

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')
    })
})
