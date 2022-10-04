describe('I can share a project', () => {
    it('', () => {
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

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')
    })
})
