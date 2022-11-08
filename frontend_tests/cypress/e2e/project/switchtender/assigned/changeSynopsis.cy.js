describe('I can change a project synopsis', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to project overview and update synopsis', () => {
        cy.contains("Reformulation du besoin")

        cy.contains('éditer').click({ force: true })

        const now = new Date();

        cy.get('textarea').clear({ force: true })

        cy.get('textarea')
            .type(`test : ${now}`)
            .should('have.value', `test : ${now}`)

        cy.contains("Enregistrer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
