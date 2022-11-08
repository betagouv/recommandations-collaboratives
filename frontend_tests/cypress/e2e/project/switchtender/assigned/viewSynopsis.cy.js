describe('I can see a project synopsis', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to project overview', () => {
        cy.contains("Reformulation du besoin")
    })
})
