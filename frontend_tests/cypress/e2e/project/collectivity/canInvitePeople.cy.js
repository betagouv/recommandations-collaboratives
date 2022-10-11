describe('I can invite people', () => {

    beforeEach(() => {
        cy.login("collectivity");
    })

    it('goes to share a project page', () => {

        cy.visit('/project/1')

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')

        cy.get('#invite-email')
            .type('ddt@test.fr', { force: true })
            .should('have.value', 'ddt@test.fr')

        cy.get('#role-collaborator').click({ force: true })

        cy.get('#invite-message')
            .type("Bonjour ddt, je t'invite à suivre mon projet frites & friches", { force: true })
            .should('have.value', "Bonjour ddt, je t'invite à suivre mon projet frites & friches")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à ddt@test.fr.");
    })
})
