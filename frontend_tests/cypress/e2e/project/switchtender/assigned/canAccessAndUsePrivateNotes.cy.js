describe('I can access and use private notes', () => {

    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to private notes', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Suivi interne").click({ force: true })

        cy.url().should('include', '/suivi')

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
