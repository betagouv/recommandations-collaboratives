describe('I can push a resource to a project', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('pushes a resource', () => {
        cy.visit('/projects')
        cy.contains("Friche numéro 1").click({force:true})
        cy.visit('/ressource/2/')
        cy.contains("Pousser la ressource").click({force:true})
        cy.get('[name="content"]')
            .type(`contenu`, { force: true })
            .should('have.value', `contenu`)

        cy.get("[type=submit]").click({ force: true });

        cy.url().should('include', '/actions')
    })
})
