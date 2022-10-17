describe('I can invite a switchtender', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to share a project page and invite a switchtender', () => {

        cy.visit('/project/2')

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')

        cy.get('#invite-email')
            .type('switchtender2@test.fr', { force: true })
            .should('have.value', 'switchtender2@test.fr')

        cy.get('#role-collaborator').click({ force: true })

        cy.get('#invite-message')
            .type("Bonjour switchtender, je t'invite à conseiller mon projet frites & friches", { force: true })
            .should('have.value', "Bonjour switchtender, je t'invite à conseiller mon projet frites & friches")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à switchtender2@test.fr");
    })
})
