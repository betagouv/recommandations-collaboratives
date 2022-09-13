describe('I can delete the fake project', () => {
    it('finds the content "type"', () => {
        cy.visit('/nimda')

        cy.get('#id_username')
            .type('qdan', { force: true })
            .should('have.value', 'qdan')

        cy.get('#id_password')
            .type('derpderp', { force: true })
            .should('have.value', 'derpderp')


        cy.contains("Connexion").click({ force: true });

        cy.contains("Projects").click({ force: true });
    })
})
