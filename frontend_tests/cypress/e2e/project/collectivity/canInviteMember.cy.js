import projects from '../../../fixtures/projects/projects.json'

const currentProject = projects[2];

describe('I can invite a member', () => {

    beforeEach(() => {
        cy.login("boba");
    })

    it('goes to the overview page and invite a member', () => {

        cy.visit(`/project/${currentProject.pk}`)

        cy.contains('Inviter un membre de la collectivité').click({ force: true });

        cy.get('#invite-member-modal').get('#invite-email')
            .type('member@test.fr', { force: true })
            .should('have.value', 'member@test.fr')

        cy.get('#invite-member-modal').get('#invite-message')
            .type("Bonjour membre, je t'invite à conseiller mon projet friche numéro 2", { force: true })
            .should('have.value', "Bonjour membre, je t'invite à conseiller mon projet friche numéro 2")


        cy.get('#invite-member-modal').contains("Envoyer l'invitation").click({force:true})
        cy.contains("Un courriel d'invitation à rejoindre le projet a été envoyé à member@test.fr")

    })
})
