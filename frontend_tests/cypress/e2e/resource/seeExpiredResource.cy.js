describe('I can see an expired resource as a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('sees an expired resource', () => {
        cy.visit('/ressource/3/')

        cy.contains("Cette ressource a expiré, les informations ne sont probablement plus à jour !")
    })
})
