describe('I can go to the dashboard and see the pending projects, and approve one', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('approves a project', () => {

        cy.visit('/projects')

        cy.contains("Projets en attente d'acceptation")
        cy.contains("Fake project name")
        cy.get("#draft-projects").siblings().contains('Fake project name')
        cy.get("#draft-projects").siblings().contains('Accepter').click({force:true})
        cy.url().should('include', '/project/')
        cy.contains("Fake Project Name")
    })
})
