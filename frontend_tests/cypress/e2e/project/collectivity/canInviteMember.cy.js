describe('I can invite a member', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to share a project page and invite a member', () => {

        cy.visit('/project/3')

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')

        cy.get('#invite-email')
            .type('bob@test.fr', { force: true })
            .should('have.value', 'bob@test.fr')

        cy.get('#role-collaborator').click({ force: true })

        cy.get('#invite-message')
            .type("Bonjour bob, je t'invite à suivre mon projet friche numéro 2", { force: true })
            .should('have.value', "Bonjour bob, je t'invite à suivre mon projet friche numéro 2")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à bob@test.fr");

        cy.contains("bob@test.fr")
        cy.contains("invité·e par boba@test.fr")
    })
})
