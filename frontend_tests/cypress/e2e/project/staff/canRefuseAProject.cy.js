describe('I can go to the dashboard and see the pending projects, and refuse one', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('refuses a project', () => {

        cy.visit('/projects')

        cy.contains("Projets en attente d'acceptation")
        cy.contains("Friche numéro 4")
        cy.get("#draft-projects").siblings().contains('Friche numéro 4').parents('tr').contains('Supprimer').click({ force: true })
        cy.url().should('include', '/projects/')
        cy.get("#draft-projects").siblings().contains('Friche numéro 4').should('not.exist')
    })
})
