describe('I can access the recommandations', () => {

    beforeEach(() => {
        cy.login("bob");
    })

    it('goes to recommandations tab and see recommandations', () => {

        cy.visit('/project/2')

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").should('not.exist')
        cy.contains("Ma ressource sans recommandation")
    })
})
