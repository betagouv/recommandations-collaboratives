describe('I can read only overview page', () => {

    beforeEach(() => {
        cy.login("jeanne");
    })

    it('goes to overview and read only content', () => {

        cy.visit('/projects')

        cy.contains('Friche numéro 1').click({force:true});

        cy.url().should('include', '/presentation')

        cy.contains("Reformulation du besoin").should('not.exist')
        cy.contains("Éditer").should('not.exist')
    })
})
