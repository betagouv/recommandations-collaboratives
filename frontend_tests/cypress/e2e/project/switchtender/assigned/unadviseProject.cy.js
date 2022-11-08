describe('I can unadvice a project', () => {
    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to overview page and unadvice a project', () => {
        cy.contains("Ne plus conseiller le projet").click({force:true})
        cy.contains("Conseiller le projet").should('exist')
    })
})
