describe('I can access and use public notes', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to public notes', () => {

        cy.visit('/project/2')

        cy.contains("Suivi interne").should('not.exist')
    })
})
