describe('I can see a non expired resource as a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('sees a non expired resource', () => {
        cy.visit('/ressource/2/')

        cy.contains("Cette ressource a une date limite fixée")
    })
})
