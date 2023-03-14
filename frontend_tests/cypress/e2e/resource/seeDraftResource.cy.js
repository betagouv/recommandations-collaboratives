describe('I can see a draft resource as a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('sees a draft resource', () => {
        cy.visit('/ressource/3/')
    })
})
