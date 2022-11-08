describe('I can see private notes', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to private notes', () => {

        cy.contains("Suivi interne").click({ force: true })

        cy.url().should('include', '/suivi')
    })
})
