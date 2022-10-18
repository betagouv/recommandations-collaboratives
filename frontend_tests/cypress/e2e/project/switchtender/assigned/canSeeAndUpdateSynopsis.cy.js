describe('I can see and update a project synopsis', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to project overview', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

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
