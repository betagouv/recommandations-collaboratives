describe('I can go to the dashboard and see the pending projects, and refuse one', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('refuses a project', () => {

        cy.visit('/projects')

        cy.contains("Projets en attente d'acceptation")
        cy.contains("Fake project name")
        cy.get("#draft-projects").siblings().contains('Fake project name')
        cy.get("#draft-projects").siblings().contains('Supprimer').click({force:true})
        cy.url().should('include', '/projects/')
    })
})
