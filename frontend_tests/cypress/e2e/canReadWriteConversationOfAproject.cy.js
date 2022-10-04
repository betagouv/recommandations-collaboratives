describe('I can read and write a conversation in a project i advise', () => {
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

        cy.get('#project-selector-button').click({ force: true });

        cy.get('#project-item').contains('Fake project name').click({ force: true })

        cy.contains("Conversation").click({ force: true })

        cy.url().should('include', '/conversations')

        const now = new Date();

        cy.get('textarea')
            .type(`test : ${now}`, { force: true })
            .should('have.value', `test : ${now}`)

        cy.contains("Envoyer").click({ force: true })

        cy.contains(`test : ${now}`)
    })
})
