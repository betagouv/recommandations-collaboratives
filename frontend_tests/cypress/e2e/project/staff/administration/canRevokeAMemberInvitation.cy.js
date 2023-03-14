import projects from '../../../../fixtures/projects/projects.json'
import users from '../../../../fixtures/users/users.json'

const currentProject = projects[1]
const userToInvite = users[6]

describe('I can go to administration area of a project and revoke an invite for a member', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to the administration tab of a project and revoke the member invitation', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('.project-navigation').children('li').contains('Administration').click({ force: true })
        cy.url().should('include', '/administration')

        cy.contains('Inviter un membre de la collectivité').click({ force: true });

        cy.get('#invite-member-modal').get('#invite-email')
            .type(`${userToInvite.fields.email}`, { force: true })
            .should('have.value', `${userToInvite.fields.email}`)

        cy.get('#invite-member-modal').get('#invite-message')
            .type(`Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet ${currentProject.fields.name}`, { force: true })
            .should('have.value', `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet ${currentProject.fields.name}`)

        cy.get('#invite-member-modal').contains("Envoyer l'invitation").click({ force: true })

        cy.contains('Invitations participant·e·s').siblings('ul').children('li').contains(userToInvite.fields.email)

        cy.contains('Invitations participant·e·s').siblings('ul').children('li').contains(userToInvite.fields.email).parent().parent().parent().siblings().find('#revoke-invite-member').click({force:true})
        cy.contains(`L'invitation de bobette@test.fr a bien été supprimée.`)
    })
})
