import projects from '../../../../fixtures/projects/projects.json'
import users from '../../../../fixtures/users/users.json'

const currentProject = projects[1]
const userToInvite = users[3]

describe('I can go to administration area of a project and send back an invite for a switchtender', () => {
    beforeEach(() => {
        cy.login("staff");
    })

    it('goes to the administration tab of a project and send back the switchtender invitation', () => {

        cy.visit(`/project/${currentProject.pk}`)
        cy.get('.project-navigation').children('li').contains('Administration').click({ force: true })
        cy.url().should('include', '/administration')

        cy.contains('Inviter un conseiller').click({ force: true });

        cy.get('.invite-switchtender-modal-email')
            .type(`${userToInvite.fields.email}`, { force: true })
            .should('have.value', `${userToInvite.fields.email}`)

        cy.get('.invite-switchtender-modal-textarea')
            .type(`Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet friche numéro 2`, { force: true })
            .should('have.value', `Bonjour ${userToInvite.fields.first_name}, je t'invite à conseiller mon projet friche numéro 2`)

        cy.get('.invite-switchtender-modal-button').click({ force: true })

        cy.contains('Invitations conseiller·e·s').siblings('ul').children('li').contains(userToInvite.fields.email)

        cy.contains('Invitations conseiller·e·s').siblings('ul').children('li').contains(userToInvite.fields.email).parent().parent().parent().siblings().find('#resend-invite-switchtender').click({force:true})
        cy.contains(`Jeannot@test.fr a bien été relancé par courriel.`)
    })
})
