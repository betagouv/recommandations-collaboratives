describe('I can create multiple recommandations with existing resources', () => {
    it('creates a reco', () => {
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

        cy.get('#project-item').contains('Fake project name').click({ force: true })

        cy.contains("Recommandations").click({ force: true })

        cy.url().should('include', '/actions')

        cy.contains("Ajouter une recommandation").click({ force: true })

        cy.get("#push-multiple").click({ force: true });

        cy.get('[x-model=search]')
            .type('test', { force: true })
            .should('have.value', 'test')

        //TODO create a ressource for that test with a given ID
        cy.get("#resource-52").click({ force: true });
        cy.get("#resource-230").click({ force: true });

        cy.contains("Enregistrer comme Brouillon").click({ force: true });

        cy.url().should('include', '/actions#action-')
    })
})
