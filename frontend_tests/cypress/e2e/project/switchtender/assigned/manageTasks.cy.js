describe('I can create a recommandation with no resource as a switcthender', () => {
    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('creates a reco', () => {

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").click({ force: true })

        cy.get("#push-noresource").click({ force: true });

        const now = new Date();

        cy.get('#intent')
            .type('fake recommandation with no resource', { force: true })
            .should('have.value', 'fake recommandation with no resource')

        cy.get('#content')
            .type(`fake recommandation content with no resource : ${now}`, { force: true })
            .should('have.value', `fake recommandation content with no resource : ${now}`)

        cy.get("[type=submit]").click({ force: true });

        cy.url().should('include', '/actions#action-')
    })
})
