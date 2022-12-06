describe('I can delete a recommandation', () => {
    beforeEach(() => {
        cy.login("jean");
    })

    it('goes to the recommandation tab, click on the recommandation and deletes it', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains('Ma ressource sans recommandation').get('#dropdownMenuLink').click({force:true})
        cy.contains('Modifier').click({force:true})

        cy.url().should('include', '/task/1/update/')

        cy.contains('Supprimer').click({force:true})
    })

    it ('checks if the recommandation is correclty deleted and not visible on the recommandation tab', () => {
        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains('Ma ressource sans recommandation').should('not.exist')
    }) 
})
