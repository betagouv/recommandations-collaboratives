describe('I can see a resource contact list if im logged', () => {
    beforeEach(() => {
    })

    it('see a contact list', () => {
        cy.visit('/ressource/3/')
        cy.contains("Nous avons des contacts associés à cette ressource. Si vous souhaitez y accéder, veuillez vous identifier.");
    })
})
