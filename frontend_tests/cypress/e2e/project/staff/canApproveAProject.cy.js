describe('I can go to the dashboard and see the pending projects, and approve one', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('approves a project', () => {

        cy.visit('/projects')

        cy.contains("Projets en attente d'acceptation")
        cy.contains("Friche numéro 3")
        cy.get("#draft-projects").siblings().contains('Friche numéro 3')
        cy.get("#draft-projects").siblings().contains('Accepter').click({force:true})
        cy.url().should('include', '/project/')
        cy.contains("Friche numéro 3")

        cy.visit('/projects')
        cy.get("#draft-projects").siblings().contains('Friche numéro 3').should('not.exist')
    })
})
