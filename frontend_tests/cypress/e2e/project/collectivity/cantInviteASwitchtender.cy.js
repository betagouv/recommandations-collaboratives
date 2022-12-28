describe('I cannot invite a switchtender as a collectivity', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to the overview page and not show the switchtender invite button', () => {

        cy.visit('/project/3')
        cy.url().should('include', '/presentation')
        cy.contains('Friche Numéro 2')
        cy.contains('Inviter un conseiller').should('not.be.visible')
    })
})
