describe('I can invite a switchtender', () => {

    beforeEach(() => {
        cy.login("jeanne");
        cy.becomeSwitchtenderOnProject('Friche numéro 1');
    })

    it('goes to overview page and invite a switchtender', () => {

        cy.contains("Inviter un conseiller").click({ force: true })

        cy.get('.invite-switchtender')
            .type('jeannot@test.fr', { force: true })
            .should('have.value', 'jeannot@test.fr')

        cy.get('.invite-message-switchtender')
            .type("Bonjour jeannot, je t'invite à conseiller mon projet friche numéro 1", { force: true })
            .should('have.value', "Bonjour jeannot, je t'invite à conseiller mon projet friche numéro 1")


        cy.get('#invite-switchtender-button').click({force:true})

        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à jeannot@test.fr.");
    })
})
