describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to public notes', () => {

        cy.visit('/project/1')

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        // cy.contains("Envoyer").should('not.exist')
    })
})
