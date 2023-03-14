describe('I can go to the dashboard and see the pending projects, and refuse one', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('refuses a project', () => {

        cy.visit('/projects')

        cy.contains("Projets en attente d'acceptation")
        cy.contains("Friche à refuser")
        cy.get("#draft-projects").siblings().contains('Friche à refuser').parents('tr').contains('Supprimer').click({ force: true })
        cy.url().should('include', '/projects/')
        cy.get("#draft-projects").siblings().contains('Friche à refuser').should('not.exist')
    })
})
