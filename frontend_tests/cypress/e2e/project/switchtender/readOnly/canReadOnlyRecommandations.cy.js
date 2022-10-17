describe('I can read only recommandations', () => {

    beforeEach(() => {
        cy.login("switchtender2");
    })

    it('goes to recommandations and read only content', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").should('not.exist')
    })
})
