describe('I can create a recommandation with an existing resource', () => {
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

        cy.get('[x-model=search]')
            .type('test', { force: true })
            .should('have.value', 'test')

        //TODO create a ressource for that test with a given ID
        cy.get("#resource-52").click({ force: true });

        const now = new Date();

        cy.get('#content')
            .type(`fake recommandation content with an existing resource : ${now}`, { force: true })
            .should('have.value', `fake recommandation content with an existing resource : ${now}`)

        cy.get("[type=submit]").click({ force: true });

        cy.url().should('include', '/actions#action-')
    })
})
