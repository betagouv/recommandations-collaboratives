describe('I can invite a member', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to overview page and invite a member', () => {

        cy.contains("Inviter un membre de la collectivité").click({ force: true })

        cy.get('#invite-email')
            .type('jeannot@test.fr', { force: true })
            .should('have.value', 'jeannot@test.fr')

        cy.get('#invite-message')
            .type("Bonjour jeannot, je t'invite à suivre mon projet friche numéro 1", { force: true })
            .should('have.value', "Bonjour jeannot, je t'invite à suivre mon projet friche numéro 1")

        cy.contains("Envoyer l'invitation").click({ force: true })

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à jeannot@test.fr.");
    })
})
