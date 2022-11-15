describe('I can see a resource contact list if im logged', () => {
    beforeEach(() => {
        cy.login("bob");
    })

    it('see a contact list', () => {
        cy.visit('/ressource/3/')

        cy.contains("Lala")
        cy.contains("Lili")
        cy.contains("Lulu")
    })
})
