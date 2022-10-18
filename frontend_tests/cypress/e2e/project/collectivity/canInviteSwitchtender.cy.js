describe('I can invite a switchtender', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to share a project page and invite a switchtender', () => {

        cy.visit('/project/3')

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')

        cy.get('#invite-email')
            .type('jeanne@test.fr', { force: true })
            .should('have.value', 'jeanne@test.fr')

        cy.get('#role-collaborator').click({ force: true })

        cy.get('#invite-message')
            .type("Bonjour jeanne, je t'invite à conseiller mon projet friche numéro 3", { force: true })
            .should('have.value', "Bonjour jeanne, je t'invite à conseiller mon projet friche numéro 3")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à jeanne@test.fr");

        cy.contains("jeanne@test.fr")
        cy.contains("invité·e par boba@test.fr")
    })
})
