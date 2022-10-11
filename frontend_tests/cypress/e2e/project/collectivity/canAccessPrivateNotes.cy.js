describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to public notes', () => {

        cy.visit('/project/1')

        cy.contains("Suivi interne").click({ force: true })

        cy.url().should('include', '/suivi')
    })
})
