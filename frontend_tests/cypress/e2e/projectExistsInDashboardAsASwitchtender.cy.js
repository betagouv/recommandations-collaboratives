describe('I can see an existing project in my dashboard', () => {
    it('finds the content "type"', () => {
        cy.visit('/')

        cy.contains('Se connecter').click({ force: true });

        cy.url().should('include', '/accounts/login/')

        cy.get('#id_login')
            .type('switchtender@email.com', { force: true })
            .should('have.value', 'switchtender@email.com')

        cy.get('#id_password')
            .type('derpderp', { force: true })
            .should('have.value', 'derpderp')

        cy.get("[type=submit]").click({ force: true });

        cy.contains("Connexion avec switchtender@email.com réussie.")

        cy.contains("Ressources").click({ force: true })

        cy.get('#project-selector-button').click({force:true});

        cy.get('#project-item').contains('Fake project name').click({force:true})

        cy.contains("Recommandations").click({force:true});
    })
})
