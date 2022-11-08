describe('I can see public notes', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to public notes', () => {

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')
    })
})
