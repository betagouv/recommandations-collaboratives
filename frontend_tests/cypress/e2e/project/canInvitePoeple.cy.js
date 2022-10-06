describe('I can see and update a project synopsis', () => {

    beforeEach(() => {
        cy.login("switchtender");
    })

    it('goes to project overview', () => {

        cy.visit('/projects')

        cy.contains('[Test] Frites & Friches 🍟').click({ force: true });

        cy.contains("Partager le détail du projet").click({ force: true })

        cy.url().should('include', '/access/')

        cy.get('#invite-email')
            .type('ddt@email.com', { force: true })
            .should('have.value', 'ddt@email.com')

        cy.get('#role-collaborator').click({ force: true })

        cy.get('#invite-message')
            .type("Bonjour ddt, je t'invite à suivre mon projet frites & friches", { force: true })
            .should('have.value', "Bonjour ddt, je t'invite à suivre mon projet frites & friches")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à ddt@email.com.");
    })
})
